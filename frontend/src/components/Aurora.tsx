// Animated ambient background: slow-drifting colored blobs behind a glass UI,
// plus a faint grid and film grain. Pure CSS animation — cheap on the GPU.
export default function Aurora() {
  return (
    <div className="aurora grain">
      <div
        className="aurora-blob animate-drift1 -left-32 -top-32 h-[42rem] w-[42rem]"
        style={{
          background:
            "radial-gradient(circle at center, #6d5cff, transparent 60%)",
        }}
      />
      <div
        className="aurora-blob animate-drift2 -right-40 top-10 h-[40rem] w-[40rem]"
        style={{
          background:
            "radial-gradient(circle at center, #b45cff, transparent 60%)",
        }}
      />
      <div
        className="aurora-blob animate-drift3 bottom-[-12rem] left-1/3 h-[38rem] w-[38rem]"
        style={{
          background:
            "radial-gradient(circle at center, #2bd4ff, transparent 60%)",
        }}
      />
      {/* faint grid */}
      <div
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage:
            "radial-gradient(ellipse at 50% 0%, black, transparent 75%)",
        }}
      />
    </div>
  );
}
