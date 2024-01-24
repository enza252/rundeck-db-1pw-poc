#/bin/python3

# get email of requesting user from rundeck: $RD_JOB_USERNAME (?)
# generate db user username: <username>
# generate credential name "<DATABASE> <ENV> <REQUESTED_USER_EMAIL> <DATETIME?>"
# check db connectivity
# check 1password connectivity - check credential doesn't already exist with name 
# create credential in 1password with <username> and generated password. Tag with "ACTIVE"
    # May need to check that the creds are present before fetching: https://github.com/1Password/connect-sdk-python/blob/cdefdd177345aeaf6e82f213f3d7f8234e7039be/example/main.py#L37
# copy or fetch the password
# create database user with the password