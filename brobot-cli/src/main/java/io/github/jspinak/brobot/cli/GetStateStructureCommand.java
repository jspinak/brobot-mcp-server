package io.github.jspinak.brobot.cli;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.github.jspinak.brobot.cli.models.StateStructureResponse;
import io.github.jspinak.brobot.cli.models.StateStructureResponse.StateInfo;
import io.github.jspinak.brobot.cli.models.StateStructureResponse.TransitionInfo;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.Callable;

/**
 * Command to get the state structure of the application.
 */
@Command(
    name = "get-state-structure",
    description = "Get the state structure of the application"
)
public class GetStateStructureCommand implements Callable<Integer> {
    
    @Option(names = {"-p", "--pretty"}, description = "Pretty print JSON output")
    private boolean prettyPrint;

    @Override
    public Integer call() {
        try {
            // TODO: Replace with actual Brobot state structure retrieval
            StateStructureResponse response = getMockStateStructure();
            
            // Convert to JSON
            Gson gson = prettyPrint 
                ? new GsonBuilder().setPrettyPrinting().create()
                : new Gson();
            
            String json = gson.toJson(response);
            System.out.println(json);
            
            return 0;
        } catch (Exception e) {
            System.err.println("Error getting state structure: " + e.getMessage());
            return 1;
        }
    }
    
    /**
     * Create mock state structure for testing.
     * TODO: Replace with actual Brobot integration.
     */
    private StateStructureResponse getMockStateStructure() {
        List<StateInfo> states = new ArrayList<>();
        
        // Main menu state
        StateInfo mainMenu = new StateInfo("main_menu", "Application main menu");
        mainMenu.setImages(Arrays.asList("main_menu_logo.png", "main_menu_title.png"));
        mainMenu.setInitial(true);
        mainMenu.setTransitions(Arrays.asList(
            new TransitionInfo("main_menu", "login_screen", "click_login", 0.95),
            new TransitionInfo("main_menu", "settings", "click_settings", 0.95)
        ));
        states.add(mainMenu);
        
        // Login screen state
        StateInfo loginScreen = new StateInfo("login_screen", "User login screen");
        loginScreen.setImages(Arrays.asList("login_form.png", "username_field.png", "password_field.png"));
        loginScreen.setTransitions(Arrays.asList(
            new TransitionInfo("login_screen", "dashboard", "submit_login", 0.90),
            new TransitionInfo("login_screen", "main_menu", "click_back", 0.95)
        ));
        states.add(loginScreen);
        
        // Dashboard state
        StateInfo dashboard = new StateInfo("dashboard", "User dashboard");
        dashboard.setImages(Arrays.asList("dashboard_header.png", "user_profile.png"));
        dashboard.setTransitions(Arrays.asList(
            new TransitionInfo("dashboard", "main_menu", "logout", 0.95)
        ));
        states.add(dashboard);
        
        // Settings state
        StateInfo settings = new StateInfo("settings", "Application settings");
        settings.setImages(Arrays.asList("settings_header.png", "settings_menu.png"));
        settings.setTransitions(Arrays.asList(
            new TransitionInfo("settings", "main_menu", "click_back", 0.95)
        ));
        states.add(settings);
        
        // Create metadata
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("application", "Sample Application");
        metadata.put("version", "1.0.0");
        metadata.put("last_updated", LocalDateTime.now().toString());
        
        return new StateStructureResponse(states, "main_menu", metadata);
    }
}