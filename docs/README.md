## Description of this folders content

- `_built`: Reference documentation is built under `_build` automatically via github continuous integration (CI) using the [gen_docs](gen_docs) script (see [.github/workflows/docs.yml](../.github/workflows/docs.yml)).  As `main`, `release/*` or `feature/*` branches are updated, pull requests are automatically created targetting these branches with updated documentation.

  Whilst running this script locally yourself might be on occasion useful perhaps, please defer from including such changes to the repository.  This is to be handled by CI.
- DAGrunner logos
  - `logo_bw.svg`: black and white logo.
  - `logo_bw_wtitle.svg`: black and white logo with title.
  - `logo.svg`: colour logo.
  - `logo_wtitle.svg`: colour logo with title.
  - `title.svg`: logo title