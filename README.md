# rundeck-db-1pw-poc

- Generate a `1password-credentials.json` file via the 1Password website.
- Run `make up`.
- Log in with `admin:admin` at `http://localhost:4040`.
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
- Configuring SCM and all that jazz is a lot of faff. Why not just call out to a custom back-end.
- Writing plugins and stuff with Java.


