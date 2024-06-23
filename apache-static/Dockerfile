FROM ubuntu:20.04

# Set non-interactive frontend and configure timezone for tzdata
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Install Apache and PHP
RUN apt-get update && \
    apt-get install -y apache2 php libapache2-mod-php && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy the website content to the Apache document root
COPY ./public-html/ /var/www/gemini.club/public_html/

# Copy the Apache virtual host configuration
COPY ./gemini.club.conf /etc/apache2/sites-available/gemini.club.conf

# Enable the site and disable the default site
RUN a2ensite gemini.club.conf && \
    a2dissite 000-default.conf

# Set ServerName globally to suppress warnings
COPY ./gemini.club.conf /etc/apache2/sites-enabled.conf/000-default.conf

# Copy the startup script
COPY start-apache.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-apache.sh

# Expose port 80
EXPOSE 80

# Start Apache in the foreground
CMD ["start-apache.sh"]
