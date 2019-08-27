FROM ubuntu:18.04

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

COPY ./apt/ /apt/

RUN apt-get update && apt-get install -y gnupg2
RUN apt-key add /apt/repo.keys
RUN cp -R /apt/sources.list* /etc/apt/
RUN apt-get update
RUN apt-get install dselect
RUN dselect update
RUN dpkg --set-selections < /apt/package.list
RUN DEBIAN_FRONTEND=noninteractive apt-get dselect-upgrade -y

COPY ./apt/requirements.txt /
RUN python3 -m pip install -r /requirements.txt --no-deps


# Copy entrypoint script and Odoo configuration file
RUN useradd --create-home --uid 1000 odoo
COPY ./entrypoint.sh /

# Make odoo runable
RUN ln -s /mnt/odoo/odoo-bin /usr/bin/odoo

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN mkdir -p /mnt/extra-addons \
        && chown -R odoo /mnt/extra-addons \
        && mkdir -p /var/lib/odoo \
        && chown -R odoo /var/lib/odoo
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf
COPY ./odoo.conf /etc/odoo/
RUN chown odoo /etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
