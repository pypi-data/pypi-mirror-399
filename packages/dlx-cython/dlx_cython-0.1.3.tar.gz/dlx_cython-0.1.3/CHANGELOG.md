# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2024-12-31

### Performance
- Fixed critical performance regression in `choose_column()` for multi-mask problems
- Optimized bit index calculation using De Bruijn sequence method (O(1) instead of O(log n))
- Sudoku performance improved from ~10ms to ~0.53ms (~19x faster)
- Bit manipulation now uses efficient multiplication/shift instead of linear search

### Fixed
- Fixed slow bit index calculation that was causing significant slowdown for problems with >64 columns
- Improved `choose_column()` efficiency for multi-mask scenarios (e.g., Sudoku with 324 columns)

## [0.1.2] - 2024-12-31

### Performance
- Optimized `choose_column()` to iterate only through active columns using efficient bit manipulation
- Extended bitmask optimization to support problems with up to 512 columns (multi-mask support)
- Improved performance for larger problems: ~6% faster for multi-mask problems (200+ columns)
- Better cache locality with optimized bit iteration

### Changed
- Bitmask optimization now automatically enabled for problems with ≤512 columns (previously ≤64)
- Multi-mask support uses up to 8 `uint64_t` masks for larger problems
- Column selection now uses bitwise iteration instead of checking all columns
- Row mask support extended to handle problems with more columns

### Fixed
- Fixed `choose_column()` inefficiency where all columns were checked instead of only active ones
- Improved bit manipulation efficiency in column selection

## [0.1.1] - 2024-XX-XX

### Added
- Bitmask optimization for problems with ≤64 columns
  - `uint64_t` bitmask replaces linked list for column headers
  - Row masks (`row_masks[64]`) for fast column covering/uncovering
  - Early row validation to skip invalid rows
  - Optimized column selection using bitwise operations

### Performance
- 1.5-4x faster for problems with ≤64 columns
- Column operations: 2-5x faster (bitwise vs pointer operations)
- Row operations: 1.5-3x faster (mask-based vs node traversal)
- Early pruning reduces unnecessary recursion
- Automatic optimization: bitmask mode for ≤64 columns, standard mode for >64 columns

### Changed
- Column selection now uses bitmask iteration for ≤64 columns
- Cover/uncover operations optimized with row masks
- Improved cache locality with array-based masks

### Fixed
- Fixed early row validation to correctly handle rows in covered columns
- All tests passing with optimizations enabled

## [0.1.0] - 2024-XX-XX

### Added
- Initial release of DLX-Cython
- Cython implementation of Dancing Links algorithm
- Python wrapper API (`DLXSolver` class)
- Support for finding first solution or all solutions
- Convenience function `solve_exact_cover()`
- Comprehensive documentation and examples
- Performance benchmarks and analysis
- Test suite

### Performance
- Sub-millisecond performance for problems up to 500x200
- Optimized with Cython compiler directives
- Efficient memory usage
