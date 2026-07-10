import React, { useEffect, useRef, useState, type ReactNode } from "react";

/** An image with a hover "expand" button that opens a zoom/pan lightbox. */
export function ExpandableImage({
  src,
  alt,
  className,
  wrapClassName,
}: {
  src: string;
  alt: string;
  className?: string;
  wrapClassName?: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`group relative ${wrapClassName ?? ""}`}>
      <img src={src} alt={alt} className={className} />
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Expand image"
        title="Expand"
        className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-lg border border-line bg-white/90 text-ink opacity-0 shadow-card backdrop-blur transition group-hover:opacity-100 focus:opacity-100"
      >
        <svg
          viewBox="0 0 24 24"
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8" />
        </svg>
      </button>
      {open && <Lightbox src={src} alt={alt} onClose={() => setOpen(false)} />}
    </div>
  );
}

function Lightbox({ src, alt, onClose }: { src: string; alt: string; onClose: () => void }) {
  const [scale, setScale] = useState(1);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [grabbing, setGrabbing] = useState(false);
  const drag = useRef<{ x: number; y: number; px: number; py: number } | null>(null);

  const clamp = (s: number) => Math.min(6, Math.max(1, s));
  const reset = () => {
    setScale(1);
    setPos({ x: 0, y: 0 });
  };
  const zoom = (d: number) =>
    setScale((s) => {
      const ns = clamp(Math.round((s + d) * 100) / 100);
      if (ns === 1) setPos({ x: 0, y: 0 });
      return ns;
    });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      else if (e.key === "+" || e.key === "=") zoom(0.4);
      else if (e.key === "-") zoom(-0.4);
      else if (e.key === "0") reset();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const onWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    zoom(e.deltaY < 0 ? 0.3 : -0.3);
  };
  const onDown = (e: React.MouseEvent) => {
    if (scale === 1) return;
    drag.current = { x: e.clientX, y: e.clientY, px: pos.x, py: pos.y };
    setGrabbing(true);
  };
  const onMove = (e: React.MouseEvent) => {
    if (!drag.current) return;
    setPos({
      x: drag.current.px + (e.clientX - drag.current.x),
      y: drag.current.py + (e.clientY - drag.current.y),
    });
  };
  const onUp = () => {
    drag.current = null;
    setGrabbing(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 p-6 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={alt}
    >
      <div
        className="absolute right-4 top-4 z-10 flex items-center gap-1.5"
        onClick={(e) => e.stopPropagation()}
      >
        <LbBtn onClick={() => zoom(-0.4)} label="Zoom out">
          -
        </LbBtn>
        <LbBtn onClick={reset} label="Reset zoom">
          {Math.round(scale * 100)}%
        </LbBtn>
        <LbBtn onClick={() => zoom(0.4)} label="Zoom in">
          +
        </LbBtn>
        <LbBtn onClick={onClose} label="Close (Esc)">
          Close
        </LbBtn>
      </div>
      <div
        className="overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        onWheel={onWheel}
        onMouseDown={onDown}
        onMouseMove={onMove}
        onMouseUp={onUp}
        onMouseLeave={onUp}
        style={{ cursor: scale > 1 ? (grabbing ? "grabbing" : "grab") : "default" }}
      >
        <img
          src={src}
          alt={alt}
          draggable={false}
          className="max-h-[88vh] max-w-[90vw] select-none rounded-lg bg-white shadow-2xl"
          style={{
            transform: `translate(${pos.x}px, ${pos.y}px) scale(${scale})`,
            transformOrigin: "center",
            transition: grabbing ? "none" : "transform 0.12s ease-out",
          }}
        />
      </div>
      <p className="pointer-events-none absolute bottom-5 left-1/2 -translate-x-1/2 text-[11.5px] text-white/70">
        scroll or +/- to zoom · drag to pan · Esc or click outside to close
      </p>
    </div>
  );
}

function LbBtn({
  children,
  onClick,
  label,
}: {
  children: ReactNode;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className="flex h-9 min-w-[36px] items-center justify-center rounded-lg border border-white/25 bg-white/10 px-2.5 text-[12px] font-semibold text-white backdrop-blur transition hover:bg-white/25"
    >
      {children}
    </button>
  );
}
