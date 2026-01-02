# Third-Party Compatibility Issues

This document tracks known compatibility issues with third-party dependencies.

## ydata-profiling + wordcloud + numpy Compatibility Issue

### Summary

When using `ydata-profiling` in non-minimal mode with DataFrames containing text columns, a `TypeError` occurs due to a compatibility issue between `wordcloud` and newer versions of `numpy`.

### Affected Versions

- **numpy**: 1.26.0+ (removed `copy` parameter from `np.asarray()`)
- **wordcloud**: 1.9.5 (still uses deprecated `copy` parameter)
- **ydata-profiling**: 4.18.0 (depends on wordcloud)

### Error Details

```
TypeError: asarray() got an unexpected keyword argument 'copy'
```

**Error Location:**
```
File ".../wordcloud/wordcloud.py", line 748, in to_array
    return np.asarray(self.to_image(), copy=copy)
```

**Call Chain:**
1. `ydata-profiling` generates word cloud visualization for text columns
2. `matplotlib` calls `imshow(wordcloud)`
3. `matplotlib.cbook.safe_masked_invalid()` calls `np.array(x, copy=copy)`
4. `wordcloud.WordCloud.__array__()` is triggered
5. `wordcloud.WordCloud.to_array(copy=copy)` calls `np.asarray(..., copy=copy)`
6. **numpy 1.26+ raises TypeError** (copy parameter was removed)

### When It Occurs

- Only in **non-minimal mode** (`minimal=False`)
- Only when the DataFrame contains **text/string columns**
- During the word cloud visualization generation step

### Workarounds

1. **Use minimal mode**: `ProfileReport(df, minimal=True)` - avoids word cloud generation
2. **Skip text columns**: Remove string columns before profiling
3. **Downgrade numpy**: Use numpy < 1.26.0 (not recommended)
4. **Wait for fix**: wordcloud library needs to update for numpy 1.26+ compatibility

### Status

- **Issue**: Known compatibility issue between wordcloud and numpy 1.26+
- **Reported**: Likely reported to wordcloud project (needs verification)
- **Our Handling**: Tests catch this exception and skip with appropriate message
- **Impact**: Affects non-minimal profiling reports with text columns only

### Related Files

- `lavendertown/profiling.py` - Profiling integration module
- `tests/test_profiling.py` - Tests handle this exception gracefully

### References

- numpy 1.26.0 release notes: Removed `copy` parameter from `np.asarray()`
- wordcloud GitHub: https://github.com/amueller/word_cloud
- ydata-profiling GitHub: https://github.com/ydataai/ydata-profiling

