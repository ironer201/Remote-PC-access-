import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";

// Define the type for your shortcuts
interface Shortcut {
  id?: number;
  value: string;
  // Add any other properties your API returns
}

export default function App() {
  // Initialize with proper type
  const [shortcuts, setShortcuts] = useState<Shortcut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://192.168.0.110:5000/shortcuts") // Update with your actual IP
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        // Type guard to validate the response
        if (data && Array.isArray(data.shortcuts)) {
          setShortcuts(data.shortcuts);
        } else {
          throw new Error("Invalid data format received");
        }
      })
      .catch(err => {
        console.log("Fetch error:", err);
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={{ color: '#fff' }}>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={{ color: '#f00' }}>Error: {error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {Array.from({ length: 6 }).map((_, i) => {
        const sc = shortcuts[i];

        return (
          <TouchableOpacity key={i}
  style={styles.button}
  onPress={() => {
    fetch("http://192.168.0.110:5000/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: sc?.id }),
    })
    .catch(err => console.log(err));
  }}
>

            <Text style={styles.title}>
              Button {String(i + 1).padStart(2, "0")}
            </Text>
            <Text style={styles.combo}>
              {sc?.value || "No shortcut"}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 20,
    backgroundColor: "#111",
  },
  button: {
    backgroundColor: "#222",
    padding: 20,
    marginVertical: 8,
    borderRadius: 10,
  },
  title: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  combo: {
    color: "#0f0",
    marginTop: 6,
    fontSize: 14,
  },
});