"use client";

import { useEffect, useRef, useState } from "react";
import { chat } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import SendIcon from "@mui/icons-material/Send";
import {
  Box,
  Card,
  CardContent,
  Divider,
  IconButton,
  Stack,
  TextField,
  Typography,
  CircularProgress, // <--- Already imported, good.
} from "@mui/material";

type Msg = { role: "user" | "assistant"; text: string };

export default function ChatCard() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  const send = async () => {
    if (!input.trim() || busy) return;
    const sid = getSessionId();
    const message = input.trim();

    // 1. Add User Message immediately
    setMsgs((m) => [...m, { role: "user", text: message }]);
    setInput("");
    setBusy(true);

    // 2. Add temporary loading message
    const tempLoadingMsg: Msg = { role: "assistant", text: "..." };
    setMsgs((m) => [...m, tempLoadingMsg]);

    try {
      const res = await chat(sid, message);

      // 3. Replace loading message with final response
      setMsgs((m) => [
        ...m.slice(0, -1), // Remove the temporary message
        { role: "assistant", text: res.answer },
      ]);
    } catch (e: any) {
      // 4. Replace loading message with error
      setMsgs((m) => [
        ...m.slice(0, -1), // Remove the temporary message
        { role: "assistant", text: e?.message ?? "Something went wrong." },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <Card variant="outlined" sx={{ borderRadius: 3, height: "100%" }}>
      <CardContent
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 2,
          height: "100%",
        }}
      >
        <Typography variant="h6">Chat</Typography>
        <Divider />
        <Box sx={{ flex: 1, overflowY: "auto", pr: 1 }}>
          <Stack spacing={1.5}>
            {msgs.map((m, i) => (
              <Box
                key={i}
                sx={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  bgcolor: m.role === "user" ? "primary.main" : "grey.200",
                  color:
                    m.role === "user" ? "primary.contrastText" : "text.primary",
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  maxWidth: "85%",
                  whiteSpace: "pre-wrap",
                  display: "flex", // Added flex for alignment
                  alignItems: "center", // Added alignment
                }}
              >
                {/* Conditionally show CircularProgress for the temporary loading message */}
                {m.role === "assistant" && m.text === "..." && busy ? (
                  <CircularProgress size={16} color="primary" sx={{ mr: 1 }} />
                ) : null}

                {/* Only render text if it's not the temporary loading indicator */}
                {m.text !== "..." ? m.text : "Thinking..."}
              </Box>
            ))}
            <div ref={bottomRef} />
          </Stack>
        </Box>

        <Stack direction="row" spacing={1}>
          <TextField
            fullWidth
            label="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={busy} // Disabled input while busy
          />
          <IconButton
            color="primary"
            onClick={send}
            disabled={busy || !input.trim()}
          >
            {/* Conditionally show CircularProgress or SendIcon */}
            {busy ? (
              <CircularProgress size={24} color="primary" />
            ) : (
              <SendIcon />
            )}
          </IconButton>
        </Stack>
      </CardContent>
    </Card>
  );
}
