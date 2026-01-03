package sample;

import java.sql.Connection;
import java.sql.Statement;
import java.sql.ResultSet;

public class InsecureUserService {

    // ❌ SECURITY: SQL Injection
    // ❌ QUALITY: No input validation
    public String getUserEmail(Connection conn, String username) throws Exception {
        Statement stmt = conn.createStatement();
        String query = "SELECT email FROM users WHERE username = '" + username + "'";
        ResultSet rs = stmt.executeQuery(query);

        if (rs.next()) {
            return rs.getString("email");
        }
        return null;
    }
}
