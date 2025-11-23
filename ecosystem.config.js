module.exports = {
    apps: [
        {
            name: "valcord",
            script: process.env.BOT_SCRIPT_PATH || "./bot.py",
            interpreter: process.env.PYTHON_INTERPRETER_PATH || "python3",
            cwd: process.env.BOT_WORKING_DIR || "./",
            env: {
                // Environment variables
            },
        },
        {
            name: "valcord-beta",
            script: process.env.BETA_BOT_SCRIPT_PATH || "./bot.py",
            interpreter: process.env.BETA_PYTHON_INTERPRETER_PATH || "python3",
            cwd: process.env.BETA_BOT_WORKING_DIR || "./",
            env: {
                BETA_MODE: "true",
            },
        }
    ],
};