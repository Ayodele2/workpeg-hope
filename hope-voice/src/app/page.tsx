"use client";

import { useEffect, useRef, useState } from "react";
import Vapi from "@vapi-ai/web";
import styles from "./page.module.css";

type TranscriptLine = {
  role: "user" | "assistant";
  text: string;
};

type CallStatus = "unconfigured" | "ready" | "connecting" | "active" | "ended" | "error";

export default function Home() {
  const vapiRef = useRef<Vapi | null>(null);
  const [status, setStatus] = useState<CallStatus>("unconfigured");
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const [error, setError] = useState("");
  const [muted, setMuted] = useState(false);

  const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY;
  const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;
  const configured = Boolean(publicKey && assistantId);

  useEffect(() => {
    if (!configured || !publicKey) {
      setStatus("unconfigured");
      return;
    }

    const vapi = new Vapi(publicKey);
    vapiRef.current = vapi;
    setStatus("ready");

    vapi.on("call-start", () => {
      setStatus("active");
      setError("");
    });

    vapi.on("call-end", () => {
      setStatus("ended");
      setMuted(false);
    });

    vapi.on("message", (message: any) => {
      if (
        message?.type === "transcript" &&
        message?.transcriptType === "final" &&
        typeof message?.transcript === "string"
      ) {
        const role = message.role === "assistant" ? "assistant" : "user";
        setTranscript((current) => [
          ...current,
          { role, text: message.transcript },
        ]);
      }
    });

    vapi.on("error", (event: any) => {
      setError(
        typeof event?.message === "string"
          ? event.message
          : "The voice connection encountered a problem. Please try again."
      );
      setStatus("error");
    });

    return () => {
      vapi.removeAllListeners();
      void vapi.stop();
      vapiRef.current = null;
    };
  }, [configured, publicKey]);

  async function startCall() {
    if (!vapiRef.current || !assistantId) return;

    setError("");
    setTranscript([]);
    setStatus("connecting");

    try {
      await vapiRef.current.start(assistantId, undefined, undefined, undefined, undefined, {
        microphonePreflightEnabled: true,
      });
    } catch (err) {
      setStatus("error");
      setError(
        err instanceof Error
          ? err.message
          : "Unable to start the voice session. Check your microphone and configuration."
      );
    }
  }

  async function endCall() {
    if (!vapiRef.current) return;

    try {
      await vapiRef.current.stop();
      setStatus("ended");
      setMuted(false);
    } catch {
      setError("The call could not be ended cleanly. Please try again.");
    }
  }

  function toggleMute() {
    if (!vapiRef.current || status !== "active") return;

    const nextMuted = !muted;
    vapiRef.current.setMuted(nextMuted);
    setMuted(nextMuted);
  }

  const statusLabel: Record<CallStatus, string> = {
    unconfigured: "Setup required",
    ready: "Ready",
    connecting: "Connecting",
    active: "Voice session active",
    ended: "Session ended",
    error: "Connection issue",
  };

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <a className={styles.brand} href="/">
          <span className={styles.brandMark}>H</span>
          <span>HOPE<span className={styles.brandLight}> Voice</span></span>
        </a>
        <span className={styles.headerTag}>EMERGENCY SUPPORT</span>
      </header>

      <section className={styles.hero}>
        <div className={styles.eyebrow}>
          <span className={styles.eyebrowDot} />
          HUMAN-FIRST EMERGENCY ASSISTANCE
        </div>

        <h1>Help starts with<br /><span>a calm voice.</span></h1>
        <p className={styles.intro}>
          Speak with the HOPE voice assistant for guided emergency intake
          and carefully scoped first-aid information while professional help
          is being arranged.
        </p>

        <div className={styles.emergencyNotice}>
          <span className={styles.noticeIcon}>!</span>
          <div>
            <strong>In an emergency, contact emergency services now.</strong>
            <p>Do not wait for this assistant or use it instead of professional medical care.</p>
          </div>
        </div>

        <section className={styles.callCard} aria-label="Voice assistant controls">
          <div className={styles.callTop}>
            <div>
              <span className={styles.sectionLabel}>HOPE ASSISTANT</span>
              <h2>How can we help?</h2>
            </div>
            <span className={`${styles.status} ${styles[status]}`}>
              <span className={styles.statusDot} />
              {statusLabel[status]}
            </span>
          </div>

          <div className={styles.voiceVisual}>
            <div className={`${styles.orb} ${status === "active" ? styles.orbActive : ""}`}>
              <span className={styles.orbCore}>H</span>
            </div>
            <p>
              {status === "active"
                ? "Listening. Speak clearly and tell us what happened."
                : status === "connecting"
                  ? "Preparing your secure voice session..."
                  : status === "unconfigured"
                    ? "Voice setup is not complete yet."
                    : "When you're ready, start a voice session."}
            </p>
          </div>

          <div className={styles.controls}>
            {status === "active" ? (
              <>
                <button className={styles.secondaryButton} onClick={toggleMute}>
                  {muted ? "Unmute microphone" : "Mute microphone"}
                </button>
                <button className={styles.endButton} onClick={endCall}>
                  End call
                </button>
              </>
            ) : (
              <button
                className={styles.startButton}
                onClick={startCall}
                disabled={!configured || status === "connecting"}
              >
                {status === "connecting" ? "Connecting..." : "Start voice session"}
                <span aria-hidden="true">→</span>
              </button>
            )}
          </div>

          {status === "unconfigured" && (
            <p className={styles.helper}>
              Add your Vapi public key and assistant ID to <code>.env.local</code>,
              then restart the development server.
            </p>
          )}

          {error && <p className={styles.error} role="alert">{error}</p>}
        </section>

        <section className={styles.transcript}>
          <div className={styles.transcriptHeading}>
            <div>
              <span className={styles.sectionLabel}>CONVERSATION</span>
              <h2>Live transcript</h2>
            </div>
            <span className={styles.privacyTag}>Not saved</span>
          </div>

          {transcript.length === 0 ? (
            <p className={styles.emptyTranscript}>
              Your conversation will appear here when the voice session begins.
            </p>
          ) : (
            <div className={styles.transcriptList} aria-live="polite">
              {transcript.map((line, index) => (
                <article className={styles.transcriptLine} key={`${index}-${line.role}`}>
                  <span className={styles.speaker}>
                    {line.role === "assistant" ? "HOPE" : "YOU"}
                  </span>
                  <p>{line.text}</p>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className={styles.disclaimer}>
          <strong>Important:</strong> This is an early development interface.
          It is not a replacement for emergency dispatch, a clinician, or
          verified first-aid training. Medical guidance must be clinically
          reviewed before real-world use.
        </div>
      </section>

      <footer className={styles.footer}>
        <span>HOPE · Emergency coordination</span>
        <span>Early development build</span>
      </footer>
    </main>
  );
}
