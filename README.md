# rundeck-db-1pw-poc

- Generate a `1password-credentials.json` file via the 1Password website.
- Run `make up`.
- Run `psql 'postgresql://dbuser\\:password@0.0.0.0:5432/sampledb'` and run `CREATE TABLE table1 ();` and `CREATE TABLE table2 ();`
- Log in to Rundeck with `admin:admin` at `http://localhost:4040`.
- Create a project manually, call it whatever.
- Create a job using `jobs/Create_User.yaml`.

## Thoughts

## Pros

- Front end work not required.
- You can write jobs as code and [import them from SCM](https://docs.rundeck.com/docs/learning/howto/how2scm.html#importing-jobs)
- You can interactively create jobs on the UI, you can export a job to YAML


## Cons

- Rundeck takes ages to boot up.
- Hosting scripts on the master / nodes isn't useful, and requires rebuild to deploy. I'm just doing this for a POC. Ideally RunDeck would be mostly stateless, and all of the exciting good _stuff_ would happen in some backend, or see SCM comment above.
- ^ We also don't want to install a bunch of dependencies on some worker nodes for the sake of automation. A well-thought through backend / API to do all of this fun stuff would be a much better development experience.
- Configuring SCM and all that jazz is a lot of faff. Why not just call out to a custom back-end.
- Writing plugins and stuff with Java.
- Could use Argo workflows, which is K8s native.
- Lots of clicking on the UI to export jobs, cognitive load to learn this stuff. Could probably, eventually, just boilerplate job yaml files.
- Not necessarily rundeck related. 1Password Connect doesn't seem to support sharing via the API, [and isn't on their roadmap](https://1password.community/discussion/127856/generate-limited-time-share-link-through-api) (the CLI does support sharing though..).
  - So, sharing credentials isn't trivial, and would still require some copy and pasting, or using the 1Password CLI in subprocess.


