"use client";

import { useRef, useState } from "react";
import { uploadFiles } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import {
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

export default function UploadCard() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>("");

  const onPick = () => inputRef.current?.click();

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const list = Array.from(e.target.files);
    setFiles(list);
  };

  const onUpload = async () => {
    if (!files.length) return;
    setLoading(true);
    setStatus("");
    try {
      const sid = getSessionId();
      const res = await uploadFiles(sid, files);
      setStatus(
        `Uploaded ${res.files_saved} file(s), indexed ${res.chunks_indexed} chunks.`
      );
      setFiles([]);
    } catch (e: any) {
      setStatus(e?.message ?? "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card variant="outlined" sx={{ borderRadius: 3 }}>
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Upload resumes</Typography>
          <Typography variant="body2" color="text.secondary">
            Accepted: .pdf, .txt — files are stored only for{" "}
            <strong>your session</strong>.
          </Typography>

          <input
            ref={inputRef}
            hidden
            type="file"
            multiple
            accept=".pdf,.txt"
            onChange={onChange}
          />

          <Stack
            direction="row"
            spacing={2}
            alignItems="center"
            flexWrap="wrap"
          >
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              onClick={onPick}
            >
              Choose files
            </Button>
            <Button
              variant="outlined"
              disabled={!files.length || loading}
              onClick={onUpload}
            >
              Upload
            </Button>
            <Typography variant="body2">
              {files.length
                ? `${files.length} file(s) selected`
                : "No files selected"}
            </Typography>
          </Stack>

          {loading && <LinearProgress />}

          {status && (
            <Box sx={{ p: 1, bgcolor: "background.default", borderRadius: 2 }}>
              <Typography variant="body2">{status}</Typography>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
