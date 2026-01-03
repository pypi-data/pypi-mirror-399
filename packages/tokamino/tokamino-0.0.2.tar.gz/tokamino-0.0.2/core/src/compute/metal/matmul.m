// =============================================================================
// Metal Matrix Multiplication - Objective-C Implementation
// =============================================================================

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <MetalPerformanceShaders/MetalPerformanceShaders.h>
#include "matmul.h"
#include "device.h"

// Import internal device structure
struct MetalDevice {
    void* device;
    void* commandQueue;
};

bool metal_matmul_f32(
    MetalDevice* ctx,
    const float* a, size_t m, size_t k,
    const float* b, size_t n,
    float* c
) {
    if (!ctx || !a || !b || !c || m == 0 || k == 0 || n == 0) return false;

    @autoreleasepool {
        id<MTLDevice> device = (__bridge id<MTLDevice>)(ctx->device);
        id<MTLCommandQueue> commandQueue = (__bridge id<MTLCommandQueue>)(ctx->commandQueue);

        // For simplicity, transpose inputs to column-major, use MPS directly, then transpose output
        // Allocate oversized buffers to account for MPS internal requirements
        size_t buf_a_size = m * k * sizeof(float) * 2;  // 2x safety margin
        size_t buf_b_size = k * n * sizeof(float) * 2;
        size_t buf_c_size = m * n * sizeof(float) * 2;

        id<MTLBuffer> bufferA = [device newBufferWithLength:buf_a_size options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufferB = [device newBufferWithLength:buf_b_size options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufferC = [device newBufferWithLength:buf_c_size options:MTLResourceStorageModeShared];

        if (!bufferA || !bufferB || !bufferC) return false;

        // Create matrix descriptors - let MPS choose rowBytes
        MPSMatrixDescriptor* descA = [MPSMatrixDescriptor
            matrixDescriptorWithRows:m
                             columns:k
                            rowBytes:0  // auto
                            dataType:MPSDataTypeFloat32];

        MPSMatrixDescriptor* descB = [MPSMatrixDescriptor
            matrixDescriptorWithRows:k
                             columns:n
                            rowBytes:0  // auto
                            dataType:MPSDataTypeFloat32];

        MPSMatrixDescriptor* descC = [MPSMatrixDescriptor
            matrixDescriptorWithRows:m
                             columns:n
                            rowBytes:0  // auto
                            dataType:MPSDataTypeFloat32];

        MPSMatrix* matrixA = [[MPSMatrix alloc] initWithBuffer:bufferA descriptor:descA];
        MPSMatrix* matrixB = [[MPSMatrix alloc] initWithBuffer:bufferB descriptor:descB];
        MPSMatrix* matrixC = [[MPSMatrix alloc] initWithBuffer:bufferC descriptor:descC];

        // Copy data (transpose row-major to column-major)
        float* a_data = (float*)[bufferA contents];
        size_t a_stride = [descA rowBytes] / sizeof(float);
        for (size_t i = 0; i < m; i++) {
            for (size_t j = 0; j < k; j++) {
                a_data[j * a_stride + i] = a[i * k + j];
            }
        }

        float* b_data = (float*)[bufferB contents];
        size_t b_stride = [descB rowBytes] / sizeof(float);
        for (size_t i = 0; i < k; i++) {
            for (size_t j = 0; j < n; j++) {
                b_data[j * b_stride + i] = b[i * n + j];
            }
        }

        // Simple matmul: C = A @ B
        MPSMatrixMultiplication* matmul = [[MPSMatrixMultiplication alloc]
            initWithDevice:device
            transposeLeft:NO
            transposeRight:NO
            resultRows:m
            resultColumns:n
            interiorColumns:k
            alpha:1.0
            beta:0.0];

        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        [matmul encodeToCommandBuffer:commandBuffer
                           leftMatrix:matrixA
                          rightMatrix:matrixB
                         resultMatrix:matrixC];

        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];

        // Copy result back (transpose column-major to row-major)
        float* c_data = (float*)[bufferC contents];
        size_t c_stride = [descC rowBytes] / sizeof(float);
        for (size_t i = 0; i < m; i++) {
            for (size_t j = 0; j < n; j++) {
                c[i * n + j] = c_data[j * c_stride + i];
            }
        }

        return true;
    }
}

// Metal shader source embedded as string (compiled at runtime)
static const char* mlx4bit_kernel_source =
#include "mlx4bit_source.h"
;

// Cache for compiled pipeline
static id<MTLComputePipelineState> g_mlx4bit_pipeline = nil;
static id<MTLDevice> g_pipeline_device = nil;

static bool ensure_mlx4bit_pipeline(id<MTLDevice> device) {
    if (g_mlx4bit_pipeline && g_pipeline_device == device) {
        return true;
    }

    NSError* error = nil;
    id<MTLLibrary> library = [device newLibraryWithSource:
        [NSString stringWithUTF8String:mlx4bit_kernel_source]
        options:nil
        error:&error];

    if (!library) {
        NSLog(@"Failed to compile Metal shader: %@", error);
        return false;
    }

    id<MTLFunction> kernel = [library newFunctionWithName:@"mlx4bit_matmul"];
    if (!kernel) {
        NSLog(@"Failed to find kernel function");
        return false;
    }

    g_mlx4bit_pipeline = [device newComputePipelineStateWithFunction:kernel error:&error];
    if (!g_mlx4bit_pipeline) {
        NSLog(@"Failed to create pipeline: %@", error);
        return false;
    }

    g_pipeline_device = device;
    return true;
}

bool metal_matmul_mlx4bit(
    MetalDevice* ctx,
    const float* a, size_t m, size_t k,
    const uint8_t* b_data,
    const uint16_t* b_scales,
    const uint16_t* b_biases,
    size_t n,
    size_t group_size,
    float* c
) {
    if (!ctx || !a || !b_data || !b_scales || !b_biases || !c) return false;

    @autoreleasepool {
        id<MTLDevice> device = (__bridge id<MTLDevice>)(ctx->device);
        id<MTLCommandQueue> commandQueue = (__bridge id<MTLCommandQueue>)(ctx->commandQueue);

        // Compile kernel on first use
        if (!ensure_mlx4bit_pipeline(device)) {
            return false;
        }

        // Create buffers
        id<MTLBuffer> bufA = [device newBufferWithBytes:a
                                                 length:m * k * sizeof(float)
                                                options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufB = [device newBufferWithBytes:b_data
                                                 length:(k * n + 1) / 2
                                                options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufScales = [device newBufferWithBytes:b_scales
                                                      length:(k * n / group_size) * sizeof(uint16_t)
                                                     options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufBiases = [device newBufferWithBytes:b_biases
                                                      length:(k * n / group_size) * sizeof(uint16_t)
                                                     options:MTLResourceStorageModeShared];
        id<MTLBuffer> bufC = [device newBufferWithLength:m * n * sizeof(float)
                                                  options:MTLResourceStorageModeShared];

        if (!bufA || !bufB || !bufScales || !bufBiases || !bufC) return false;

        // Encode compute command
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];

        [encoder setComputePipelineState:g_mlx4bit_pipeline];
        [encoder setBuffer:bufA offset:0 atIndex:0];
        [encoder setBuffer:bufB offset:0 atIndex:1];
        [encoder setBuffer:bufScales offset:0 atIndex:2];
        [encoder setBuffer:bufBiases offset:0 atIndex:3];
        [encoder setBuffer:bufC offset:0 atIndex:4];

        uint32_t params[4] = {(uint32_t)m, (uint32_t)k, (uint32_t)n, (uint32_t)group_size};
        [encoder setBytes:&params[0] length:sizeof(uint32_t) atIndex:5];
        [encoder setBytes:&params[1] length:sizeof(uint32_t) atIndex:6];
        [encoder setBytes:&params[2] length:sizeof(uint32_t) atIndex:7];
        [encoder setBytes:&params[3] length:sizeof(uint32_t) atIndex:8];

        // Dispatch threads: one thread per output element
        MTLSize gridSize = MTLSizeMake(n, m, 1);
        NSUInteger threadGroupSize = g_mlx4bit_pipeline.maxTotalThreadsPerThreadgroup;
        NSUInteger w = 16;  // threads per group in x
        NSUInteger h = threadGroupSize / w;  // threads per group in y
        MTLSize threadgroupSize = MTLSizeMake(w, h, 1);

        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
        [encoder endEncoding];

        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];

        // Copy result back
        memcpy(c, [bufC contents], m * n * sizeof(float));

        return true;
    }
}
