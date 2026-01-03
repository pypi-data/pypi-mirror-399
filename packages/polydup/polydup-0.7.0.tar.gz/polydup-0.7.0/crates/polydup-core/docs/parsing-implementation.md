# Tree-sitter Parsing Implementation Summary

## Completed

### Module: `src/queries.rs`
- **Purpose**: Tree-sitter S-expression query definitions
- **Implementation**: Uses `once_cell::Lazy` for compile-time query initialization
- **Queries Defined**:
  - `RUST_QUERY`: Extracts `function_item` and impl methods
  - `PYTHON_QUERY`: Extracts `function_definition`
  - `JAVASCRIPT_QUERY`: Extracts `function_declaration`, `method_definition`, and `arrow_function`

### Module: `src/parsing.rs`
- **Core Type**: `FunctionNode`
  - Fields: `start_byte`, `end_byte`, `body: String`, `name: Option<String>`
  - Methods: `new()`, `with_name()`, `len()`, `is_empty()`

- **Core Function**: `extract_functions(code: &str, lang: Language) -> Result<Vec<FunctionNode>>`
  - Creates Tree-sitter parser with specified language grammar
  - Compiles and executes language-specific query
  - Extracts function nodes with byte ranges and bodies
  - Handles captures: `@func`, `@function.name`, `@function.body`

- **Convenience Functions**:
  - `extract_rust_functions(code: &str)`
  - `extract_python_functions(code: &str)`
  - `extract_javascript_functions(code: &str)`

### Language Grammar Integration
- `tree-sitter-rust`: Via `tree_sitter_rust::language()`
- `tree-sitter-python`: Via `tree_sitter_python::language()`
- `tree-sitter-javascript`: Via `tree_sitter_javascript::language()`

## Testing

All 10 unit tests pass:
- Query validation (non-empty, contains captures)
- Rust function extraction (2 functions + 1 impl method)
- Python function extraction (2 functions + 1 method)
- JavaScript function extraction (function declaration + arrow function + class method)
- Edge cases: empty code, invalid syntax

### Test Results
```bash
cargo test -p polydup-core
# running 10 tests
# test result: ok. 10 passed; 0 failed
```

### Demo Example
```bash
cargo run -p polydup-core --example parse_demo
```

Output demonstrates successful parsing of:
- 4 Rust functions (including impl block methods)
- 3 Python functions
- 3 JavaScript functions

## API Usage

```rust
use dupe_core::{extract_rust_functions, FunctionNode};

let code = r#"
fn hello() {
    println!("Hello!");
}
"#;

let functions = extract_rust_functions(code)?;
for func in functions {
    println!("{}: {} bytes",
        func.name.unwrap(),
        func.len()
    );
}
```

## Architecture Notes

### Language Detection Strategy
- Uses `is_same_language()` helper to compare Tree-sitter `Language` instances
- Compares version and node_kind_count as proxy for equality (since `Language` doesn't implement `PartialEq`)

### Error Handling
- All functions return `anyhow::Result`
- Contextual errors via `.context()`
- Handles UTF-8 validation for extracted text

### Performance Considerations
- Queries compiled once per call (could be cached globally in future)
- Zero-copy where possible (byte ranges instead of copying strings)
- Ready for parallel processing with Rayon in Scanner

## Next Steps

To integrate into `Scanner::scan()`:
1. Detect file language by extension
2. Read file contents
3. Call appropriate `extract_*_functions()`
4. Extract function bodies for hashing
5. Proceed to Rabin-Karp/MinHash duplicate detection

## Dependencies Added

```toml
once_cell = "1.19"  # For lazy static query initialization
```
