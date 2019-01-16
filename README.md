# grow-ext-greenhouse

[![Build
Status](https://travis-ci.org/grow/grow-ext-greenhouse.svg?branch=master)](https://travis-ci.org/grow/grow-ext-greenhouse)

An extension to integrate Greenhouse data with Grow. Provides a way to
serialize Greenhouse jobs into YAML files and a backend proxy for submitting
job applications.

## Concept

Greenhouse is an applicant tracking system and hiring tool for organizations to recruit and hire candidates. The Grow extension leverages the Greenhouse API so job listings can be embedded within a Grow website.

## Usage

### Grow setup

1. Create an `extensions.txt` file within your pod.
1. Add to the file: `git+git://github.com/grow/grow-ext-greenhouse`
1. Run `grow install`.
1. Add the following section to `podspec.yaml`:

```
extensions:
  preprocessors:
  - extensions.greenhouse.GreenhousePreprocessor

preprocessors:
- kind: greenhouse
  board_token: <token>
  jobs_collection: /content/jobs
```

The preprocessor accepts a few additional configuration options, see
`example/podspec.yaml` for examples.

### Configuration

1. Acquire the `board_token` from the
   (Greenhouse Dev Center)[https://app.greenhouse.io/configure/dev_center/config/].

### Developer notes

- See [Greenhouse Job Board API
  documentation](https://developers.greenhouse.io/job-board.html) for more
  details.
