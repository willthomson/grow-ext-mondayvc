# grow-ext-mondayvc

An extension to integrate Monday.vc data with Grow. Provides a way to serialize Monday.vc jobs into YAML files.

## Concept

Monday.vc is an applicant tracking system and hiring tool for organizations to recruit and hire candidates. The Grow extension leverages the Monday.vc API so job listings can be embedded within a Grow website.

## Usage

### Grow setup

1. Create an `extensions.txt` file within your pod.
1. Add to the file: `git+git://github.com/grow/grow-ext-mondayvc`
1. Run `grow install`.
1. Add the following section to `podspec.yaml`:

```
extensions:
  preprocessors:
  - extensions.mondayvc.MondayVCPreprocessor

preprocessors:
- kind: mondayvc
  api_user: test@gmail.com
  api_key: <mondayvc-api-key>
  collections_id: <collection-id>  // Required for jobs & organizations API calls
  jobs_path: /content/partials/jobs.yaml
  collections_path: /content/partials/collections.yaml
  organizations_path: /content/partials/organizations.yaml
```

The preprocessor accepts a few additional configuration options, see
`example/podspec.yaml` for examples.

### Configuration

1. Monday expects for the User email and the API key to be included in all API requests to the server in a header that looks like the following:
```
X-User-Email: test@email.com
X-User-Token: <mondayvc-api-key>
Content-Type: application/json
Accept: application/json
```

### Developer notes

- See [Monday.vc API
  documentation](https://docs.monday.vc/) for more
  details.
