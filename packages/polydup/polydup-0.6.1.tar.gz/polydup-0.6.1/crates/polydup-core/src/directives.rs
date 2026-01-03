//! Inline directive detection for suppressing false positives
//!
//! This module provides support for inline comments that suppress duplicate
//! detection warnings directly in source code, similar to linter directives.
//!
//! # Supported Directive Formats
//!
//! ## JavaScript/TypeScript/Rust
//! ```javascript
//! // polydup-ignore: intentional code reuse
//! function duplicateCode() { ... }
//! ```
//!
//! ## Python
//! ```python
//! # polydup-ignore: framework boilerplate
//! def duplicate_function():
//!     pass
//! ```
//!
//! # Detection Strategy
//!
//! Directives are detected by scanning comment lines immediately before
//! a function or code block. The directive suppresses duplicate detection
//! for the entire function/block that follows it.

use std::collections::HashMap;
use std::path::Path;

/// Represents a directive found in source code
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Directive {
    /// Line number where the directive appears (1-indexed)
    pub line: usize,
    /// Optional reason provided in the directive
    pub reason: Option<String>,
}

/// Directive detection result for a single file
#[derive(Debug, Clone)]
pub struct FileDirectives {
    /// Map of line numbers to directives
    /// Key: Line number where suppression applies (function start line)
    /// Value: The directive that applies
    directives: HashMap<usize, Directive>,
}

impl FileDirectives {
    /// Creates an empty directive set
    pub fn new() -> Self {
        Self {
            directives: HashMap::new(),
        }
    }

    /// Checks if a line range is suppressed by a directive
    ///
    /// A directive suppresses a range if it appears within 3 lines before
    /// the start of the range (allowing for blank lines).
    ///
    /// # Arguments
    /// * `start_line` - Starting line of the code block (1-indexed)
    /// * `end_line` - Ending line of the code block (1-indexed)
    ///
    /// # Returns
    /// * `Some(Directive)` - If the range is suppressed
    /// * `None` - If no directive applies
    pub fn is_suppressed(&self, start_line: usize, _end_line: usize) -> Option<&Directive> {
        // Check the function start line and up to 3 lines before it
        // This allows for blank lines and multi-line comments between directive and function
        for offset in 0..=3 {
            if start_line > offset {
                let check_line = start_line - offset;
                if let Some(directive) = self.directives.get(&check_line) {
                    return Some(directive);
                }
            }
        }

        None
    }

    /// Adds a directive for a specific line
    fn add_directive(&mut self, line: usize, directive: Directive) {
        self.directives.insert(line, directive);
    }

    /// Returns the number of directives in this file
    pub fn len(&self) -> usize {
        self.directives.len()
    }

    /// Checks if there are any directives
    pub fn is_empty(&self) -> bool {
        self.directives.is_empty()
    }
}

impl Default for FileDirectives {
    fn default() -> Self {
        Self::new()
    }
}

/// Detects polydup-ignore directives in source code
///
/// Scans for comment lines containing "polydup-ignore" and extracts
/// optional reasons.
///
/// # Supported Formats
/// - `// polydup-ignore` (no reason)
/// - `// polydup-ignore: reason here`
/// - `# polydup-ignore: reason here` (Python)
///
/// # Arguments
/// * `source` - The source code to scan
///
/// # Returns
/// * `FileDirectives` - Detected directives with line numbers
pub fn detect_directives(source: &str) -> FileDirectives {
    let mut directives = FileDirectives::new();
    let lines: Vec<&str> = source.lines().collect();

    for (i, line) in lines.iter().enumerate() {
        let line_num = i + 1; // 1-indexed
        let trimmed = line.trim();

        // Check for polydup-ignore directive in comments
        if let Some(directive) = parse_directive_line(trimmed) {
            // Store the directive at the line where it appears
            // The is_suppressed() method will handle checking nearby lines
            directives.add_directive(line_num, directive);
        }
    }

    directives
}

/// Parses a single line to detect a polydup-ignore directive
///
/// # Arguments
/// * `line` - A trimmed line of source code
///
/// # Returns
/// * `Some(Directive)` - If the line contains a valid directive
/// * `None` - If no directive is found
fn parse_directive_line(line: &str) -> Option<Directive> {
    // Check for JavaScript/TypeScript/Rust style comments
    if let Some(rest) = line.strip_prefix("//") {
        return parse_comment_content(rest, line.len());
    }

    // Check for Python style comments
    if let Some(rest) = line.strip_prefix('#') {
        return parse_comment_content(rest, line.len());
    }

    None
}

/// Extracts directive information from comment content
fn parse_comment_content(content: &str, _line_len: usize) -> Option<Directive> {
    let content = content.trim();

    // Check for exact match or with colon
    if let Some(rest) = content.strip_prefix("polydup-ignore") {
        let rest = rest.trim();

        // Extract reason if provided after colon
        let reason = if let Some(after_colon) = rest.strip_prefix(':') {
            let r = after_colon.trim();
            if r.is_empty() {
                None
            } else {
                Some(r.to_string())
            }
        } else if rest.is_empty() {
            None
        } else {
            // If there's content but no colon, treat it as reason
            Some(rest.to_string())
        };

        return Some(Directive {
            line: 0, // Will be set by caller
            reason,
        });
    }

    None
}

/// Detects directives in a file
///
/// # Arguments
/// * `path` - Path to the source file
///
/// # Returns
/// * `Result<FileDirectives>` - Detected directives or error
pub fn detect_directives_in_file(path: &Path) -> anyhow::Result<FileDirectives> {
    let source = std::fs::read_to_string(path)?;
    Ok(detect_directives(&source))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_javascript_directive_with_reason() {
        let source = r#"
// polydup-ignore: intentional code reuse
function duplicate() {
    console.log("test");
}
"#;
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 1);

        // Directive is at line 2
        assert!(directives.is_suppressed(2, 5).is_some());
        assert!(directives.is_suppressed(3, 5).is_some()); // Function start should also match
    }

    #[test]
    fn test_detect_python_directive() {
        let source = r#"
# polydup-ignore: framework requirement
def duplicate_function():
    pass
"#;
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 1);
        assert!(directives.is_suppressed(2, 4).is_some());
    }

    #[test]
    fn test_directive_without_reason() {
        let source = "// polydup-ignore\nfunction test() {}";
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 1);

        let directive = directives.is_suppressed(1, 2).unwrap();
        assert!(directive.reason.is_none());
    }

    #[test]
    fn test_directive_with_colon_but_no_reason() {
        let source = "// polydup-ignore:\nfunction test() {}";
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 1);

        let directive = directives.is_suppressed(1, 2).unwrap();
        assert!(directive.reason.is_none());
    }

    #[test]
    fn test_no_directive() {
        let source = r#"
// This is just a regular comment
function not_ignored() {
    return 42;
}
"#;
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 0);
        assert!(directives.is_suppressed(2, 5).is_none());
    }

    #[test]
    fn test_multiple_directives() {
        let source = r#"
// polydup-ignore: reason 1
function fn1() {}

// polydup-ignore: reason 2
function fn2() {}
"#;
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 2);

        assert!(directives.is_suppressed(2, 3).is_some());
        assert!(directives.is_suppressed(5, 6).is_some());
    }

    #[test]
    fn test_rust_directive() {
        let source = r#"
// polydup-ignore: generated code
fn duplicate() -> i32 {
    42
}
"#;
        let directives = detect_directives(source);
        assert_eq!(directives.len(), 1);
        assert!(directives.is_suppressed(2, 5).is_some());
    }
}
