"use client";

import { useRef, useState } from "react";

type Props = {
  onFile: (file: File) => void;
  previewUrl: string | null;
  previewFilter: string;
  disabled?: boolean;
};

export function DropZone({ onFile, previewUrl, previewFilter, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  function accept(file: File | undefined | null) {
    if (!file || disabled) return;
    if (!file.type.startsWith("image/")) return;
    onFile(file);
  }

  return (
    <div
      className={`dropzone ${dragOver ? "dragover" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        accept(e.dataTransfer.files?.[0]);
      }}
    >
      {!previewUrl ? (
        <div className="dropzone-prompt">
          <div className="upload-orbit" aria-hidden="true">
            <span>＋</span>
          </div>
          <h3>Drop an image here</h3>
          <p>We&apos;ll describe it and begin narration automatically.</p>
          <button
            className="primary-button"
            type="button"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
          >
            Choose an image
          </button>
          <span className="file-hint">PNG, JPG or WEBP · processed locally</span>
        </div>
      ) : null}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        hidden
        aria-label="Choose image file"
        onChange={(e) => accept(e.target.files?.[0])}
      />
      {previewUrl ? (
        <div className="preview-wrap">
          <div className={`preview-frame ${previewFilter}`} aria-label="Image preview">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={previewUrl} alt="Uploaded content preview" />
            <span className="preview-badge">Current image</span>
          </div>
          <button
            className="replace-button"
            type="button"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
          >
            Replace image
          </button>
        </div>
      ) : null}
    </div>
  );
}
