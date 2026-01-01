public class SecurityAndPerformanceExamples {

    // --- Security Bug: String-concatenated SQL ---
    public String insecureSql(String user) {
        return "SELECT * FROM accounts WHERE username = '" + user + "'";
    }

    // --- Performance Bug: Inefficient Loop ---
    public void slowLoop(int[] arr) {
        for (int i : arr) {
            for (int j : arr) {
                if (i == j) {
                    // do something
                }
            }
        }
    }

    public void fastLoop(int[] arr) {
        java.util.HashSet<Integer> set = new java.util.HashSet<>();
        for (int i : arr) set.add(i);

        for (int i : arr) {
            if (set.contains(i)) {
                // do something
            }
        }
    }
}
