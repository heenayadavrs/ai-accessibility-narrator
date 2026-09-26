"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Segment } from "./api";

export type PlayerState = {
  index: number;
  playing: boolean;
  rate: number;
  statusText: string;
};

export function useNarrationPlayer(segments: Segment[]) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [rate, setRate] = useState(1);
  const [statusText, setStatusText] = useState("Ready");

  const total = segments.length;

  const loadAndPlay = useCallback(
    async (i: number) => {
      if (!segments.length) return;
      const seg = segments[i];
      if (!seg?.audio_url) {
        setStatusText("No audio for this segment");
        return;
      }
      if (!audioRef.current) {
        audioRef.current = new Audio();
      }
      const audio = audioRef.current;
      audio.pause();
      audio.src = seg.audio_url;
      audio.playbackRate = rate;
      setIndex(i);
      setStatusText(`Playing section ${i + 1} of ${total}`);
      try {
        await audio.play();
        setPlaying(true);
      } catch {
        setPlaying(false);
        setStatusText("Playback blocked — press Play");
      }
    },
    [segments, rate, total]
  );

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onEnded = () => {
      setPlaying(false);
      if (index < total - 1) {
        void loadAndPlay(index + 1);
      } else {
        setStatusText("Finished narration");
      }
    };
    audio.addEventListener("ended", onEnded);
    return () => audio.removeEventListener("ended", onEnded);
  }, [index, total, loadAndPlay]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
    }
  }, [rate]);

  useEffect(() => {
    // Reset when segments change
    setIndex(0);
    setPlaying(false);
    setStatusText(segments.length ? `Loaded ${segments.length} segments` : "Ready");
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.removeAttribute("src");
    }
  }, [segments]);

  const play = useCallback(() => {
    void loadAndPlay(index);
  }, [loadAndPlay, index]);

  const pause = useCallback(() => {
    audioRef.current?.pause();
    setPlaying(false);
    setStatusText("Paused");
  }, []);

  const toggle = useCallback(() => {
    if (playing) pause();
    else play();
  }, [playing, pause, play]);

  const next = useCallback(() => {
    if (index < total - 1) void loadAndPlay(index + 1);
  }, [index, total, loadAndPlay]);

  const prev = useCallback(() => {
    if (index > 0) void loadAndPlay(index - 1);
    else void loadAndPlay(0);
  }, [index, loadAndPlay]);

  const playAnswer = useCallback(
    async (url: string) => {
      if (!audioRef.current) audioRef.current = new Audio();
      const audio = audioRef.current;
      audio.pause();
      audio.src = url;
      audio.playbackRate = rate;
      setStatusText("Playing answer");
      try {
        await audio.play();
        setPlaying(true);
      } catch {
        setPlaying(false);
      }
    },
    [rate]
  );

  return {
    index,
    playing,
    rate,
    setRate,
    statusText,
    play,
    pause,
    toggle,
    next,
    prev,
    playAnswer,
    total,
  };
}
