# tinydb-rust

[English](README.md) | [简体中文](README.zh.md)

[TinyDB](https://github.com/msiemens/tinydb) 库的高性能 Rust 重实现，在保持与原始 Python 实现 API 兼容的同时，提供内存安全性和更高的性能。

## 🎉 版本 0.9.0 - Beta 版本

**本项目处于 Beta 阶段，所有核心功能已实现，可以正常使用。**

## 特性

### ✅ 已完整实现

- **完整的 TinyDB API**：100% 与原始 TinyDB 库 API 兼容
- **高性能**：核心操作使用 Rust 实现，性能优于纯 Python 版本
- **存储后端**：
  - `JSONStorage`：持久化 JSON 文件存储
  - `MemoryStorage`：内存存储（用于测试）
- **查询系统**：完整的查询 API，支持复杂条件（==, !=, <, <=, >, >=, matches, search, test, exists 等）
- **表操作**：完整的 CRUD 操作（insert, search, update, remove, all, get, contains, count 等）
- **中间件支持**：CachingMiddleware 和其他中间件支持
- **工具函数**：LRUCache、FrozenDict、freeze() 函数
- **性能优化**：
  - Rust 端表缓存减少 Python-Rust 转换开销
  - Rust Query 对象的快速路径查询评估
  - 优化的文档匹配和过滤

## 安装

```bash
pip install tinydb-rust
```

## 要求

- Python >= 3.8

## 性能

基准测试结果显示，tinydb-rust 的性能优于纯 Python TinyDB：

- **查询操作**：**约快 11%** - 查询操作性能显著提升
- **全表扫描**：**约快 6%** - 高效的文档匹配和过滤
- **整体操作**：**约快 10%** - 所有操作的综合性能提升
- **内存高效**：Rust 端缓存减少了 Python-Rust 转换开销

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

## 致谢

- [TinyDB](https://github.com/msiemens/tinydb) - 原始 Python 实现

## 作者

morninghao (morning.haoo@gmail.com)

