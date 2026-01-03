//! Integration tests for inline directive detection and suppression

use dupe_core::{detect_directives, Scanner};
use std::fs;
use tempfile::TempDir;

/// Test that directives are correctly detected in source code
#[test]
fn test_directive_detection_basic() {
    let source = r#"
// polydup-ignore: test reason
function test() {
    return 42;
}
"#;

    let directives = detect_directives(source);
    assert_eq!(directives.len(), 1, "Should detect one directive");
    assert!(
        directives.is_suppressed(2, 5).is_some(),
        "Should suppress function at line 2"
    );
}

/// Test that Scanner correctly marks duplicates as suppressed when directives are present
#[test]
fn test_directive_suppresses_javascript_duplicate() {
    let temp_dir = TempDir::new().unwrap();
    let base_path = temp_dir.path();

    let file1_path = base_path.join("file1.js");
    let file2_path = base_path.join("file2.js");

    // Create longer functions that exceed the 50-token minimum
    let duplicate_code = r#"
function processData(input) {
    const data = Array.isArray(input) ? input : [input];
    const filtered = data.filter(item => item != null && item != undefined);
    const mapped = filtered.map(item => {
        if (typeof item === 'string') {
            return item.toUpperCase().trim();
        } else if (typeof item === 'number') {
            return item * 2 + 10;
        } else {
            return String(item);
        }
    });
    const result = mapped.reduce((acc, val) => {
        if (acc.length === 0) {
            return [val];
        }
        return [...acc, val];
    }, []);
    console.log("Processed result:", result);
    return result;
}
"#;

    // File1 with directive
    fs::write(
        &file1_path,
        format!(
            "// polydup-ignore: intentional code reuse\n{}",
            duplicate_code
        ),
    )
    .unwrap();

    // File2 without directive
    fs::write(&file2_path, duplicate_code).unwrap();

    // Scan without directives - should find duplicate
    let scanner = Scanner::new();
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();
    let duplicates_without_directives = report.duplicates.len();
    assert!(
        duplicates_without_directives > 0,
        "Should find duplicates without directive detection"
    );

    // Scan with directives - should filter out suppressed duplicates
    let scanner = Scanner::new().with_directives(true);
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();

    // Suppressed duplicates should be filtered out (not just marked)
    assert!(
        report.duplicates.len() < duplicates_without_directives,
        "Should have fewer duplicates with directives enabled (suppressed ones filtered out)"
    );

    // Verify no duplicates are marked as suppressed (they should be removed entirely)
    assert!(
        !report
            .duplicates
            .iter()
            .any(|d| d.suppressed_by_directive == Some(true)),
        "Suppressed duplicates should be filtered out, not just marked"
    );
}

#[test]
fn test_directive_suppresses_python_duplicate() {
    let temp_dir = TempDir::new().unwrap();
    let base_path = temp_dir.path();

    let file1_path = base_path.join("file1.py");
    let file2_path = base_path.join("file2.py");

    let python_code = r#"
def calculate_stats(numbers):
    if not numbers or len(numbers) == 0:
        return None
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    sorted_nums = sorted(numbers)
    middle = count // 2
    if count % 2 == 0:
        median = (sorted_nums[middle - 1] + sorted_nums[middle]) / 2
    else:
        median = sorted_nums[middle]
    min_val = min(numbers)
    max_val = max(numbers)
    range_val = max_val - min_val
    return {
        'mean': mean,
        'median': median,
        'min': min_val,
        'max': max_val,
        'range': range_val
    }
"#;

    fs::write(
        &file1_path,
        format!("# polydup-ignore: framework boilerplate\n{}", python_code),
    )
    .unwrap();
    fs::write(&file2_path, python_code).unwrap();

    // Scan without directives first
    let scanner_no_directives = Scanner::new();
    let report_no_directives = scanner_no_directives
        .scan(vec![base_path.to_path_buf()])
        .unwrap();
    let duplicates_without_directives = report_no_directives.duplicates.len();

    // Scan with directives enabled
    let scanner = Scanner::new().with_directives(true);
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();

    // With Python directive, duplicates should be filtered out
    if duplicates_without_directives > 0 {
        assert!(
            report.duplicates.len() < duplicates_without_directives,
            "Python directive should filter out suppressed duplicates"
        );

        // No duplicates should be marked as suppressed (they're filtered out)
        assert!(
            !report
                .duplicates
                .iter()
                .any(|d| d.suppressed_by_directive == Some(true)),
            "Suppressed duplicates should be filtered out, not marked"
        );
    }
}

/// Regression test: Directive should suppress duplicates deep in function
/// Previously, suppression was checked against the duplicate's start line,
/// not the function start line. This caused duplicates appearing more than
/// 3 lines into a function to ignore the directive.
#[test]
fn test_directive_suppresses_deep_duplicate_in_function() {
    let temp_dir = TempDir::new().unwrap();
    let base_path = temp_dir.path();

    let file1_path = base_path.join("file1.js");
    let file2_path = base_path.join("file2.js");

    // Create a function where the duplicate code appears DEEP in the function
    // (more than 3 lines from the directive)
    let file1_content = r#"// polydup-ignore: intentional duplicate
function processData(input) {
    // Setup code - multiple lines before the duplicate
    const config = {};
    const options = { enabled: true };
    let result = null;
    let counter = 0;

    // The duplicate code starts here - well past line 3
    const data = Array.isArray(input) ? input : [input];
    const filtered = data.filter(item => item != null && item != undefined);
    const mapped = filtered.map(item => {
        if (typeof item === 'string') {
            return item.toUpperCase().trim();
        } else if (typeof item === 'number') {
            return item * 2 + 10;
        } else {
            return String(item);
        }
    });
    return mapped;
}
"#;

    // File2 has the same duplicate code without directive
    let file2_content = r#"function processData(input) {
    const data = Array.isArray(input) ? input : [input];
    const filtered = data.filter(item => item != null && item != undefined);
    const mapped = filtered.map(item => {
        if (typeof item === 'string') {
            return item.toUpperCase().trim();
        } else if (typeof item === 'number') {
            return item * 2 + 10;
        } else {
            return String(item);
        }
    });
    return mapped;
}
"#;

    fs::write(&file1_path, file1_content).unwrap();
    fs::write(&file2_path, file2_content).unwrap();

    // Scan without directives - should find duplicates
    let scanner = Scanner::new();
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();
    let duplicates_without_directives = report.duplicates.len();

    // Scan with directives - should suppress even though duplicate is deep in function
    let scanner = Scanner::new().with_directives(true);
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();

    // The directive should suppress duplicates ANYWHERE in the function,
    // not just within 3 lines of the directive
    assert!(
        report.duplicates.len() < duplicates_without_directives
            || duplicates_without_directives == 0,
        "Directive should suppress duplicates deep in function. \
         Without directives: {}, With directives: {}. \
         This indicates the fix for checking function start line is not working.",
        duplicates_without_directives,
        report.duplicates.len()
    );
}

#[test]
fn test_directives_disabled_no_suppression() {
    let temp_dir = TempDir::new().unwrap();
    let base_path = temp_dir.path();

    let file_path = base_path.join("with_directive.js");

    fs::write(
        &file_path,
        r#"
// polydup-ignore
function test() {
    console.log("Has directive but disabled");
    return 1;
}

function test2() {
    console.log("Has directive but disabled");
    return 1;
}
"#,
    )
    .unwrap();

    // Scanner with directives DISABLED (default)
    let scanner = Scanner::new();
    let report = scanner.scan(vec![base_path.to_path_buf()]).unwrap();

    // When directives are disabled, suppressed_by_directive should be None
    for dup in &report.duplicates {
        assert_eq!(
            dup.suppressed_by_directive, None,
            "Should not mark as suppressed when directives disabled"
        );
    }
}
