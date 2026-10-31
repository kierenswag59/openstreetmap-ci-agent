# frozen_string_literal: true

# Raise the memcached client socket timeout in development.
Rails.application.config.x.memcache_socket_timeout = 1.5 if Rails.env.development?
