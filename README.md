# grow-ext-greenhouse

[![Build
Status](https://travis-ci.org/grow/grow-ext-greenhouse.svg?branch=master)](https://travis-ci.org/grow/grow-ext-greenhouse)

(WIP) An extension to integrate Greenhouse data with Grow. Provides a way to
serialize Greenhouse jobs into YAML files and a backend proxy for submitting
job applications.

## Concept

(WIP)

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

### Configuration

1. Acquire the `board_token` from the
   [https://app.greenhouse.io/configure/dev_center/config/](Greenhouse Dev
   Center).

### Developer notes

- See [Greenhouse Job Board API
  documentation](https://developers.greenhouse.io/job-board.html) for more
  details.
