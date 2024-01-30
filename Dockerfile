ARG RUNDECK_IMAGE
FROM ${RUNDECK_IMAGE}


RUN sudo apt-get update && \
     sudo apt-get install -y -qq --no-install-recommends wget git curl jq iputils-ping sysstat python3 python3-pip

RUN ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa <<< y

COPY --chown=rundeck:root data/resources.yml /home/rundeck
COPY data/realm.properties /home/rundeck/server/config
COPY data/plugins/. /home/rundeck/libext
COPY scripts/ /home/rundeck/scripts/

# Not ideal to do this, but it's less hassle
RUN pip3 install psycopg2-binary onepasswordconnectsdk