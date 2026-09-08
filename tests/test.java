import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class PerformanceTest {
    @Test
    void calculateDensityAltitude_returnsExpectedValue() {
        double result = Performance.calculateDensityAltitude(2500, 25);
        assertEquals(4300, result, 1);
    }
}