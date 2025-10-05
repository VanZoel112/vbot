/**
 * VZ ASSISTANT v0.0.0.69
 * PM2 Ecosystem Configuration - Multi-User Sudoer Management
 *
 * 2025© Vzoel Fox's Lutpan
 * Founder & DEVELOPER : @VZLfxs
 *
 * This file is auto-generated and managed by deploybot.py
 * Each sudoer runs as a separate PM2 process with isolated session
 */

module.exports = {
  apps: [
    {
      name: 'vz-deploybot',
      script: 'deploybot.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/deploybot-error.log',
      out_file: './logs/deploybot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
    // Sudoer processes will be dynamically added here by deploybot
    // Format:
    // {
    //   name: 'vz-sudoer-<user_id>',
    //   script: 'run_sudoer.py',
    //   interpreter: 'python3',
    //   args: '<user_id>',
    //   instances: 1,
    //   autorestart: true,
    //   max_memory_restart: '500M',
    //   env: {
    //     USER_ID: '<user_id>',
    //     SESSION_STRING: '<session_string>'
    //   }
    // }
  ]
};
