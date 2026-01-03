# tinydb-rust

[English](README.md) | [简体中文](README.zh.md)

A high-performance Rust reimplementation of the [TinyDB](https://github.com/msiemens/tinydb) library, providing memory safety and improved performance while maintaining API compatibility with the original Python implementation.

## 🎉 Version 0.9.0 - Beta Release

**This project is in Beta and ready for use. All core TinyDB functionality is implemented.**

## Features

### ✅ Fully Implemented

- **Complete TinyDB API**: 100% API compatible with the original TinyDB library
- **High Performance**: Core operations implemented in Rust, providing better performance than pure Python
- **Storage Backends**:
  - `JSONStorage`: Persistent JSON file storage
  - `MemoryStorage`: In-memory storage for testing
- **Query System**: Full query API with support for complex conditions (==, !=, <, <=, >, >=, matches, search, test, exists, etc.)
- **Table Operations**: Complete CRUD operations (insert, search, update, remove, all, get, contains, count, etc.)
- **Middleware Support**: CachingMiddleware and other middleware support
- **Utilities**: LRUCache, FrozenDict, freeze() function
- **Performance Optimizations**:
  - Rust-side table caching to reduce Python-Rust conversions
  - Fast-path query evaluation for Rust Query objects
  - Optimized document matching and filtering

## Installation

```bash
pip install tinydb-rust
```

## Requirements

- Python >= 3.8

## Performance

Benchmark results demonstrate that tinydb-rust delivers improved performance compared to the pure Python TinyDB:

- **Search operations**: **~11% faster** - Query operations show significant improvement
- **Full table scans**: **~6% faster** - Efficient document matching and filtering
- **Overall operations**: **~10% faster** - Balanced performance across all operations
- **Memory efficient**: Rust-side caching reduces Python-Rust conversion overhead

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [TinyDB](https://github.com/msiemens/tinydb) - The original Python implementation

## Author

morninghao (morning.haoo@gmail.com)
