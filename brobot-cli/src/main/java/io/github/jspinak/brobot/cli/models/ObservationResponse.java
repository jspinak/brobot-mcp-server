package io.github.jspinak.brobot.cli.models;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Response model for observation command.
 */
public class ObservationResponse {
    private String timestamp;
    private List<ActiveState> activeStates;
    private String screenshot;  // Base64 encoded
    private int screenWidth;
    private int screenHeight;
    private Map<String, Object> metadata;

    public ObservationResponse(String timestamp, List<ActiveState> activeStates, 
                              String screenshot, int screenWidth, int screenHeight,
                              Map<String, Object> metadata) {
        this.timestamp = timestamp;
        this.activeStates = activeStates;
        this.screenshot = screenshot;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.metadata = metadata;
    }

    // Getters and setters
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    
    public List<ActiveState> getActiveStates() { return activeStates; }
    public void setActiveStates(List<ActiveState> activeStates) { this.activeStates = activeStates; }
    
    public String getScreenshot() { return screenshot; }
    public void setScreenshot(String screenshot) { this.screenshot = screenshot; }
    
    public int getScreenWidth() { return screenWidth; }
    public void setScreenWidth(int screenWidth) { this.screenWidth = screenWidth; }
    
    public int getScreenHeight() { return screenHeight; }
    public void setScreenHeight(int screenHeight) { this.screenHeight = screenHeight; }
    
    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    
    /**
     * Active state information.
     */
    public static class ActiveState {
        private String name;
        private double confidence;
        private List<String> matchedPatterns;

        public ActiveState(String name, double confidence, List<String> matchedPatterns) {
            this.name = name;
            this.confidence = confidence;
            this.matchedPatterns = matchedPatterns;
        }

        // Getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public double getConfidence() { return confidence; }
        public void setConfidence(double confidence) { this.confidence = confidence; }
        
        public List<String> getMatchedPatterns() { return matchedPatterns; }
        public void setMatchedPatterns(List<String> matchedPatterns) { this.matchedPatterns = matchedPatterns; }
    }
}