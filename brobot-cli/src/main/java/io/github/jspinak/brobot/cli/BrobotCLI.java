package io.github.jspinak.brobot.cli;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.util.concurrent.Callable;

/**
 * Main CLI entry point for Brobot MCP integration.
 * Provides commands to interact with Brobot's automation engine.
 */
@Command(
    name = "brobot-cli",
    mixinStandardHelpOptions = true,
    version = "brobot-cli 0.1.0",
    description = "CLI wrapper for Brobot automation framework",
    subcommands = {
        GetStateStructureCommand.class,
        GetObservationCommand.class,
        ExecuteActionCommand.class
    }
)
public class BrobotCLI implements Callable<Integer> {

    @Option(names = {"-v", "--verbose"}, description = "Enable verbose logging")
    private boolean verbose;

    @Override
    public Integer call() {
        System.err.println("Please specify a command. Use --help for available commands.");
        return 1;
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new BrobotCLI()).execute(args);
        System.exit(exitCode);
    }
}