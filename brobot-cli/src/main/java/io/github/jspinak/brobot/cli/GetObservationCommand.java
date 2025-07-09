package io.github.jspinak.brobot.cli;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.github.jspinak.brobot.cli.models.ObservationResponse;
import io.github.jspinak.brobot.cli.models.ObservationResponse.ActiveState;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.time.LocalDateTime;
import java.util.*;
import java.util.List;
import java.util.concurrent.Callable;

/**
 * Command to get current observation of the application.
 */
@Command(
    name = "get-observation",
    description = "Get current observation including screenshot and active states"
)
public class GetObservationCommand implements Callable<Integer> {
    
    @Option(names = {"-p", "--pretty"}, description = "Pretty print JSON output")
    private boolean prettyPrint;
    
    @Option(names = {"-s", "--screenshot"}, description = "Include screenshot in response", defaultValue = "true")
    private boolean includeScreenshot;

    @Override
    public Integer call() {
        try {
            // TODO: Replace with actual Brobot observation
            ObservationResponse response = getMockObservation();
            
            // Convert to JSON
            Gson gson = prettyPrint 
                ? new GsonBuilder().setPrettyPrinting().create()
                : new Gson();
            
            String json = gson.toJson(response);
            System.out.println(json);
            
            return 0;
        } catch (Exception e) {
            System.err.println("Error getting observation: " + e.getMessage());
            return 1;
        }
    }
    
    /**
     * Create mock observation for testing.
     * TODO: Replace with actual Brobot integration.
     */
    private ObservationResponse getMockObservation() throws Exception {
        // Active states
        List<ActiveState> activeStates = Arrays.asList(
            new ActiveState("main_menu", 0.95, Arrays.asList("main_menu_logo.png", "main_menu_title.png")),
            new ActiveState("login_screen", 0.15, Collections.emptyList())
        );
        
        // Get screen dimensions (mock)
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        int screenWidth = (int) screenSize.getWidth();
        int screenHeight = (int) screenSize.getHeight();
        
        // Create mock screenshot
        String screenshot = "";
        if (includeScreenshot) {
            screenshot = createMockScreenshot();
        }
        
        // Metadata
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("capture_duration", 0.125);
        metadata.put("analysis_duration", 0.087);
        metadata.put("total_patterns_checked", 12);
        
        return new ObservationResponse(
            LocalDateTime.now().toString(),
            activeStates,
            screenshot,
            screenWidth,
            screenHeight,
            metadata
        );
    }
    
    /**
     * Create a mock screenshot for testing.
     * Creates a simple 1x1 transparent PNG.
     */
    private String createMockScreenshot() throws Exception {
        // Create a 1x1 transparent image
        BufferedImage image = new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB);
        image.setRGB(0, 0, 0x00000000);
        
        // Convert to Base64
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ImageIO.write(image, "png", baos);
        byte[] imageBytes = baos.toByteArray();
        
        return Base64.getEncoder().encodeToString(imageBytes);
    }
}