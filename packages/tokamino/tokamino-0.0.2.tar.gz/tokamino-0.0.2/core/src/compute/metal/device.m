// =============================================================================
// Metal Device Management - Objective-C Implementation
// =============================================================================

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include "device.h"

struct MetalDevice {
    void* device;
    void* commandQueue;
};

struct MetalBuffer {
    void* buffer;
    size_t size;
};

bool metal_is_available(void) {
    return MTLCopyAllDevices() != nil && [MTLCopyAllDevices() count] > 0;
}

MetalDevice* metal_device_create(void) {
    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (!device) {
            return NULL;
        }

        id<MTLCommandQueue> commandQueue = [device newCommandQueue];
        if (!commandQueue) {
            return NULL;
        }

        MetalDevice* ctx = (MetalDevice*)malloc(sizeof(MetalDevice));
        ctx->device = (__bridge_retained void*)device;
        ctx->commandQueue = (__bridge_retained void*)commandQueue;

        return ctx;
    }
}

void metal_device_destroy(MetalDevice* device) {
    if (!device) return;

    @autoreleasepool {
        if (device->commandQueue) {
            CFRelease(device->commandQueue);
        }
        if (device->device) {
            CFRelease(device->device);
        }
        free(device);
    }
}

const char* metal_device_name(MetalDevice* device) {
    if (!device || !device->device) return "Unknown";

    @autoreleasepool {
        id<MTLDevice> mtl_device = (__bridge id<MTLDevice>)(device->device);
        return [[mtl_device name] UTF8String];
    }
}

MetalBuffer* metal_buffer_create(MetalDevice* device, size_t size) {
    if (!device || !device->device || size == 0) return NULL;

    @autoreleasepool {
        id<MTLDevice> mtl_device = (__bridge id<MTLDevice>)(device->device);
        id<MTLBuffer> buffer = [mtl_device newBufferWithLength:size
                                                       options:MTLResourceStorageModeShared];
        if (!buffer) return NULL;

        MetalBuffer* mb = (MetalBuffer*)malloc(sizeof(MetalBuffer));
        mb->buffer = (__bridge_retained void*)buffer;
        mb->size = size;

        return mb;
    }
}

void metal_buffer_upload(MetalBuffer* buffer, const void* data, size_t size) {
    if (!buffer || !buffer->buffer || !data) return;

    @autoreleasepool {
        id<MTLBuffer> mtl_buffer = (__bridge id<MTLBuffer>)(buffer->buffer);
        size_t copy_size = size < buffer->size ? size : buffer->size;
        memcpy([mtl_buffer contents], data, copy_size);
    }
}

void metal_buffer_download(MetalBuffer* buffer, void* data, size_t size) {
    if (!buffer || !buffer->buffer || !data) return;

    @autoreleasepool {
        id<MTLBuffer> mtl_buffer = (__bridge id<MTLBuffer>)(buffer->buffer);
        size_t copy_size = size < buffer->size ? size : buffer->size;
        memcpy(data, [mtl_buffer contents], copy_size);
    }
}

void* metal_buffer_contents(MetalBuffer* buffer) {
    if (!buffer || !buffer->buffer) return NULL;

    @autoreleasepool {
        id<MTLBuffer> mtl_buffer = (__bridge id<MTLBuffer>)(buffer->buffer);
        return [mtl_buffer contents];
    }
}

void metal_buffer_destroy(MetalBuffer* buffer) {
    if (!buffer) return;

    @autoreleasepool {
        if (buffer->buffer) {
            CFRelease(buffer->buffer);
        }
        free(buffer);
    }
}

void metal_device_synchronize(MetalDevice* device) {
    if (!device || !device->commandQueue) return;

    @autoreleasepool {
        id<MTLCommandQueue> queue = (__bridge id<MTLCommandQueue>)(device->commandQueue);
        id<MTLCommandBuffer> commandBuffer = [queue commandBuffer];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
    }
}
