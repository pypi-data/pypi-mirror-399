.PHONY: all deps build wasm static python clean clean-deps test graphs docs curl-build mlx-build mbedtls-build lint

all: build

deps:
	# macOS: requires `brew install cmake` (Xcode Command Line Tools for Metal)
	@test -d deps/utf8proc || git clone --branch v2.11.2 --depth 1 https://github.com/JuliaStrings/utf8proc.git deps/utf8proc
	@test -d deps/pcre2 || git clone --branch pcre2-10.47 --depth 1 https://github.com/PCRE2Project/pcre2.git deps/pcre2
	@test -d deps/curl || git clone --branch curl-8_17_0 --depth 1 https://github.com/curl/curl.git deps/curl
ifneq ($(shell uname -s),Darwin)
	@test -d deps/mbedtls || (git clone --branch v3.6.2 --depth 1 --recurse-submodules https://github.com/Mbed-TLS/mbedtls.git deps/mbedtls)
	@test -f deps/mbedtls/build/library/libmbedtls.a || $(MAKE) mbedtls-build
endif
	@test -f deps/curl/build/lib/libcurl.a || $(MAKE) curl-build
ifeq ($(shell uname -s),Darwin)
	@test -f deps/mlx/lib/libmlx.a || $(MAKE) mlx-build
endif

mbedtls-build:
	@echo "Building mbedTLS static library..."
	@mkdir -p deps/mbedtls/build
	@cd deps/mbedtls/build && cmake .. \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
		-DENABLE_TESTING=OFF \
		-DENABLE_PROGRAMS=OFF \
		-DMBEDTLS_FATAL_WARNINGS=OFF
	@cd deps/mbedtls/build && cmake --build . --config Release -j$$(nproc 2>/dev/null || sysctl -n hw.ncpu)
	@echo "mbedTLS installed to deps/mbedtls/build/library/"

mlx-build:
	# Build MLX static library (macOS only, requires Xcode >= 15.0)
	@echo "Building MLX static library..."
	@test -d deps/mlx-src || git clone --branch v0.30.1 --depth 1 https://github.com/ml-explore/mlx.git deps/mlx-src
	@mkdir -p deps/mlx-src/build
	@cd deps/mlx-src/build && cmake .. \
		-DCMAKE_BUILD_TYPE=Release \
		-DBUILD_SHARED_LIBS=OFF \
		-DMLX_BUILD_TESTS=OFF \
		-DMLX_BUILD_EXAMPLES=OFF \
		-DMLX_BUILD_BENCHMARKS=OFF \
		-DMLX_BUILD_PYTHON_BINDINGS=OFF \
		-DMLX_BUILD_METAL=ON \
		-DMLX_BUILD_CPU=ON \
		-DMLX_METAL_JIT=ON
	@cd deps/mlx-src/build && cmake --build . --config Release -j$$(sysctl -n hw.ncpu)
	@echo "Installing MLX to deps/mlx..."
	@mkdir -p deps/mlx/lib deps/mlx/include
	@cp deps/mlx-src/build/libmlx.a deps/mlx/lib/
	@rm -rf deps/mlx/include/mlx
	@cp -r deps/mlx-src/mlx deps/mlx/include/
	@echo "MLX v0.30.1 (JIT mode) installed to deps/mlx/"

curl-build:
	@echo "Building libcurl with CMake (HTTP-only, minimal)..."
	@mkdir -p deps/curl/build
ifeq ($(shell uname -s),Darwin)
	@cd deps/curl/build && cmake .. \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
		-DBUILD_SHARED_LIBS=OFF \
		-DBUILD_CURL_EXE=OFF \
		-DBUILD_TESTING=OFF \
		-DHTTP_ONLY=ON \
		-DCURL_USE_SECTRANSPORT=ON \
		-DCURL_USE_OPENSSL=OFF \
		-DCURL_USE_LIBPSL=OFF \
		-DCURL_USE_LIBSSH2=OFF \
		-DCURL_ZLIB=OFF \
		-DUSE_LIBIDN2=OFF \
		-DUSE_NGHTTP2=OFF \
		-DCURL_BROTLI=OFF \
		-DCURL_ZSTD=OFF \
		-DCURL_DISABLE_ALTSVC=ON \
		-DCURL_DISABLE_COOKIES=OFF \
		-DCURL_DISABLE_DOH=ON \
		-DCURL_DISABLE_GETOPTIONS=ON \
		-DCURL_DISABLE_HSTS=ON \
		-DCURL_DISABLE_MIME=ON \
		-DCURL_DISABLE_NETRC=ON \
		-DCURL_DISABLE_NTLM=ON \
		-DCURL_DISABLE_PROGRESS_METER=ON \
		-DCURL_DISABLE_PROXY=OFF \
		-DCURL_DISABLE_VERBOSE_STRINGS=ON \
		-DCURL_DISABLE_WEBSOCKETS=ON \
		-DCURL_DISABLE_IPFS=ON \
		-DCURL_DISABLE_FORM_API=ON \
		-DCURL_DISABLE_HEADERS_API=ON \
		-DCURL_DISABLE_BINDLOCAL=ON \
		-DCURL_DISABLE_DIGEST_AUTH=ON \
		-DCURL_DISABLE_BEARER_AUTH=ON \
		-DCURL_DISABLE_KERBEROS_AUTH=ON \
		-DCURL_DISABLE_NEGOTIATE_AUTH=ON \
		-DCURL_DISABLE_AWS=ON \
		-DCURL_DISABLE_SRP=ON
else
	@cd deps/curl/build && cmake .. \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
		-DBUILD_SHARED_LIBS=OFF \
		-DBUILD_CURL_EXE=OFF \
		-DBUILD_TESTING=OFF \
		-DHTTP_ONLY=ON \
		-DCURL_USE_OPENSSL=OFF \
		-DCURL_USE_MBEDTLS=ON \
		-DMBEDTLS_INCLUDE_DIRS=$(CURDIR)/deps/mbedtls/include \
		-DMBEDTLS_LIBRARY=$(CURDIR)/deps/mbedtls/build/library/libmbedtls.a \
		-DMBEDX509_LIBRARY=$(CURDIR)/deps/mbedtls/build/library/libmbedx509.a \
		-DMBEDCRYPTO_LIBRARY=$(CURDIR)/deps/mbedtls/build/library/libmbedcrypto.a \
		-DCURL_USE_LIBPSL=OFF \
		-DCURL_USE_LIBSSH2=OFF \
		-DCURL_ZLIB=OFF \
		-DUSE_LIBIDN2=OFF \
		-DUSE_NGHTTP2=OFF \
		-DCURL_BROTLI=OFF \
		-DCURL_ZSTD=OFF \
		-DCURL_DISABLE_ALTSVC=ON \
		-DCURL_DISABLE_COOKIES=OFF \
		-DCURL_DISABLE_DOH=ON \
		-DCURL_DISABLE_GETOPTIONS=ON \
		-DCURL_DISABLE_HSTS=ON \
		-DCURL_DISABLE_MIME=ON \
		-DCURL_DISABLE_NETRC=ON \
		-DCURL_DISABLE_NTLM=ON \
		-DCURL_DISABLE_PROGRESS_METER=ON \
		-DCURL_DISABLE_PROXY=OFF \
		-DCURL_DISABLE_VERBOSE_STRINGS=ON \
		-DCURL_DISABLE_WEBSOCKETS=ON \
		-DCURL_DISABLE_IPFS=ON \
		-DCURL_DISABLE_FORM_API=ON \
		-DCURL_DISABLE_HEADERS_API=ON \
		-DCURL_DISABLE_BINDLOCAL=ON \
		-DCURL_DISABLE_DIGEST_AUTH=ON \
		-DCURL_DISABLE_BEARER_AUTH=ON \
		-DCURL_DISABLE_KERBEROS_AUTH=ON \
		-DCURL_DISABLE_NEGOTIATE_AUTH=ON \
		-DCURL_DISABLE_AWS=ON \
		-DCURL_DISABLE_SRP=ON
endif
	@cd deps/curl/build && cmake --build . --config Release -j$$(nproc 2>/dev/null || sysctl -n hw.ncpu)

build: deps
	zig build -Drelease -Dcpu=native
	@cp zig-out/lib/libtokamino.so tokamino/ 2>/dev/null || true

wasm: deps
	zig build wasm -Drelease

static: deps
	zig build static -Drelease -Dcpu=native

test: deps
	zig build test -Drelease -Dcpu=native

lint:
	uv run ruff check tokamino/ tests/
	uv run ruff format --check tokamino/ tests/
	uv run pytest tests/linter/ -v

python: build
	cp zig-out/lib/libtokamino.so tokamino/
	uv sync && uv build

# Compute graph files in tokamino/_graphs/
# Generated from readable Python models in models/
GRAPHS_DIR = tokamino/_graphs

graphs:
	@echo "Generating graph files from Python models..."
	cd models && uv sync
	cd models && .venv/bin/python -m trace --all
	@echo ""
	@ls -la $(GRAPHS_DIR)/*.json

docs:
	uv run python docs/_build/build.py

clean:
	rm -rf zig-out .zig-cache .zig-cache-global
	rm -f tokamino/libtokamino.so
	rm -rf dist .venv
	rm -rf deps/curl/build
	rm -rf deps/mlx-src/build
	rm -rf deps/mbedtls/build

clean-deps:
	rm -rf deps/
