# PolyDup Core Documentation

Implementation documentation for the core duplicate detection library.

## Contents

- [parsing-implementation.md](parsing-implementation.md) - Tree-sitter parsing, language detection, and AST traversal
- [hashing-implementation.md](hashing-implementation.md) - Rabin-Karp rolling hash and Hash-and-Extend algorithm

## Architecture

The `polydup-core` crate is the heart of PolyDup, providing:

1. **Language Detection**: File extension to Tree-sitter grammar mapping
2. **Parsing**: AST generation via Tree-sitter for JavaScript, TypeScript, Python, Rust, Vue, Svelte
3. **Token Normalization**: Converting AST nodes to normalized token streams (Type-2 clone detection)
4. **Hashing**: Rabin-Karp rolling hash for efficient fingerprinting
5. **Duplicate Detection**: Hash-and-Extend algorithm for maximal duplicate regions
6. **Reporting**: Structured output with similarity scores and source locations

## Key Data Structures

### Scanner

The main entry point for duplicate detection:

```rust
pub struct Scanner {
    parsers: DashMap<String, Parser>,
    min_block_size: usize,
    similarity_threshold: f64,
}
```

Thread-safe parser pool with configuration options.

### DuplicateMatch

Detection result:

```rust
pub struct DuplicateMatch {
    pub file1: String,
    pub file2: String,
    pub start_line1: usize,
    pub start_line2: usize,
    pub length: usize,
    pub similarity: f64,
    pub hash: u64,
}
```

### Report

Scan results with statistics:

```rust
pub struct Report {
    pub files_scanned: usize,
    pub functions_analyzed: usize,
    pub duplicates: Vec<DuplicateMatch>,
    pub stats: ScanStats,
}
```

## Algorithm Flow

1. **File Discovery**: Recursively scan directories for supported file types
2. **Parallel Parsing**: Process files concurrently using `rayon`
3. **Token Extraction**: Convert AST to normalized token streams
4. **Hashing**: Generate rolling hashes for all k-length windows
5. **Collision Detection**: Group identical hashes to find candidates
6. **Extension**: Expand matches bidirectionally using Hash-and-Extend
7. **Filtering**: Remove subsumed duplicates and apply threshold
8. **Reporting**: Aggregate results with statistics

## Performance Characteristics

- **Time Complexity**: O(n) for parsing + hashing, O(m log m) for collision grouping
- **Space Complexity**: O(n) for token storage, O(k) for hash map
- **Parallelism**: File-level parallelism via `rayon` thread pool
- **Memory**: Streaming token processing, no full file buffering

## Testing

The core library has comprehensive test coverage:

- **Unit tests**: Individual function and struct tests
- **Snapshot tests**: Golden file comparison via `insta`
- **Property tests**: Fuzz testing with `proptest`
- **Clone detection tests**: Type-1, Type-2, Type-3 clone scenarios

Run tests:

```bash
cargo test -p polydup-core
cargo test -p polydup-core --test clone_detection_tests
```

## Future Enhancements

- **MinHash LSH**: For approximate similarity on large codebases
- **Incremental scanning**: Cache parsed ASTs between runs
- **More languages**: Java, Go, C/C++, Ruby, PHP via Tree-sitter grammars
- **Semantic clones**: Type-4 detection using program dependence graphs
