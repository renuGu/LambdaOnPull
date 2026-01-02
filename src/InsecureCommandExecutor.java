package sample;

public class InsecureCommandExecutor {

    // ❌ SECURITY: Command Injection
    // ❌ UPTIME: Runtime.exec() can hang process
    public void pingHost(String host) throws Exception {
        String command = "ping -c 4 " + host;
        Runtime.getRuntime().exec(command);
    }
}
