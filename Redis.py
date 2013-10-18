#!/usr/bin/env python


import re
import commands


class Redis:
    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.redis_config = raw_config.get('Redis') if raw_config else None

    def run(self):
        stats = {}
        status, out = commands.getstatusoutput(self.redis_cmd_prefix() + 'info')
        if status != 0:
            return stats
        # Grab every statistic available and leave it to the end user to
        # determine which fields they care about
        for key, val in [line.split(':') for line in out.splitlines()]:
            stats[key] = val

        # Collect lens for each queue in config (if any)
        if self.redis_config and self.redis_config.get('queues'):
            self.checks_logger.debug('Found Redis queues list in config')
            for queue in self.redis_config['queues'].split(','):
                queue_name, db = queue.strip().split('@', 2)
                db_number = db.replace('db', '')
                status, out = commands.getstatusoutput('%s -n %s llen %s' %
                    (self.redis_cmd_prefix(), db_number, queue_name))
                if status != 0:
                    continue
                stats[queue] = out.replace('(integer) ', out)
        return stats

    def redis_cmd_prefix(self):
        if self.redis_config and self.redis_config.get('password'):
            self.checks_logger.debug('Found Redis password in config')
            return 'redis-cli -a %s ' % self.redis_config['password']
        else:
            return 'redis-cli '


if __name__ == '__main__':
    redis = Redis(None, None, None)
    print redis.run()
