# Citation formats

## APA 7

Journal article:

```text
Author, A. A., & Author, B. B. (Year). Article title. Journal Title, volume(issue), pages. https://doi.org/...
```

Use sentence case for English article titles. Preserve the source language of Chinese titles and names unless the user requests transliteration.

## GB/T 7714—2015

Journal article:

```text
作者. 题名[J]. 刊名, 年, 卷(期): 页码. DOI.
```

Online resource:

```text
作者. 题名[EB/OL]. (发布日期)[引用日期]. URL.
```

Do not add unavailable volume, issue, page, DOI, or publication-place fields.

## BibTeX

```bibtex
@article{key,
  author  = {...},
  title   = {...},
  journal = {...},
  year    = {...},
  volume  = {...},
  number  = {...},
  pages   = {...},
  doi     = {...}
}
```

Escape BibTeX-special characters and retain Unicode unless the requested toolchain requires LaTeX transliteration.

