/**
 * Unit tests for MobilePanel component.
 * Mocks sidecar mobile methods — no real sidecar required.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MobilePanel } from "../../src/components/MobilePanel";

vi.mock("../../src/lib/sidecar", () => ({
  sidecar: {
    mobileTooling: vi.fn(),
    mobileDevices: vi.fn(),
    mobileSimulatorBoot: vi.fn(),
    mobileEmulatorStart: vi.fn(),
    mobileAppiumStart: vi.fn(),
    mobileAppiumStop: vi.fn(),
    mobileAppiumStatus: vi.fn(),
  },
}));

import { sidecar } from "../../src/lib/sidecar";

const mockTools = {
  tools: [
    { name: "adb", available: true, path: "/usr/local/bin/adb" },
    { name: "xcrun", available: true, path: "/usr/bin/xcrun" },
    { name: "appium", available: false, path: null },
    { name: "emulator", available: false, path: null },
  ],
};

const mockDevices = {
  devices: [
    {
      id: "emulator-5554",
      name: "Pixel_6_API_33",
      platform: "android" as const,
      state: "offline",
    },
    {
      id: "00001111-AAAA-BBBB-CCCC-000011112222",
      name: "iPhone 15 Pro",
      platform: "ios" as const,
      state: "Shutdown",
    },
  ],
};

const mockAppiumStopped = { running: false, port: 4723 };
const mockAppiumRunning = { running: true, port: 4723, detail: "Appium v2.0" };

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(sidecar.mobileTooling).mockResolvedValue(mockTools);
  vi.mocked(sidecar.mobileDevices).mockResolvedValue(mockDevices);
  vi.mocked(sidecar.mobileSimulatorBoot).mockResolvedValue({ message: "Booting" });
  vi.mocked(sidecar.mobileEmulatorStart).mockResolvedValue({ message: "Starting" });
  vi.mocked(sidecar.mobileAppiumStart).mockResolvedValue({ port: 4723, pid: 12345, message: "Appium started" });
  vi.mocked(sidecar.mobileAppiumStop).mockResolvedValue({ message: "Stopped" });
  vi.mocked(sidecar.mobileAppiumStatus).mockResolvedValue(mockAppiumStopped);
});

// ---------------------------------------------------------------------------
// Tooling dots
// ---------------------------------------------------------------------------

describe("MobilePanel — tooling", () => {
  it("renders tool names from mocked tooling response", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() => expect(screen.getByText("adb")).toBeInTheDocument());
    expect(screen.getByText("xcrun")).toBeInTheDocument();
    expect(screen.getByText("appium")).toBeInTheDocument();
    expect(screen.getByText("emulator")).toBeInTheDocument();
  });

  it("shows availability dots for available and unavailable tools", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() => expect(screen.getByText("adb")).toBeInTheDocument());

    // 2 available (adb, xcrun) → aria-label "Dostupný"; 2 unavailable → "Nedostupný"
    const available = screen.getAllByLabelText("Dostupný");
    const unavailable = screen.getAllByLabelText("Nedostupný");
    expect(available.length).toBe(2);
    expect(unavailable.length).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// Device list
// ---------------------------------------------------------------------------

describe("MobilePanel — devices", () => {
  it("renders device rows from mocked devices response", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByText("Pixel_6_API_33")).toBeInTheDocument(),
    );
    expect(screen.getByText("iPhone 15 Pro")).toBeInTheDocument();
  });

  it("shows platform badges for each device", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByText("Pixel_6_API_33")).toBeInTheDocument(),
    );
    expect(screen.getByText("Android")).toBeInTheDocument();
    expect(screen.getByText("iOS")).toBeInTheDocument();
  });

  it("shows Start button for Android offline device", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByText("Pixel_6_API_33")).toBeInTheDocument(),
    );
    // Android offline → "Start"; iOS shutdown → "Boot"
    expect(screen.getByTitle(/Start Pixel_6_API_33/)).toBeInTheDocument();
    expect(screen.getByTitle(/Boot iPhone 15 Pro/)).toBeInTheDocument();
  });

  it("clicking refresh calls mobileDevices again", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByText("Pixel_6_API_33")).toBeInTheDocument(),
    );

    // Should have been called once on mount
    expect(vi.mocked(sidecar.mobileDevices)).toHaveBeenCalledTimes(1);

    await userEvent.click(screen.getByRole("button", { name: /Obnovit/i }));

    await waitFor(() =>
      expect(vi.mocked(sidecar.mobileDevices)).toHaveBeenCalledTimes(2),
    );
  });

  it("calls mobileEmulatorStart when Start is clicked for Android", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByTitle(/Start Pixel_6_API_33/)).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByTitle(/Start Pixel_6_API_33/));

    await waitFor(() =>
      expect(vi.mocked(sidecar.mobileEmulatorStart)).toHaveBeenCalledWith(
        "Pixel_6_API_33",
      ),
    );
  });

  it("calls mobileSimulatorBoot when Boot is clicked for iOS", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByTitle(/Boot iPhone 15 Pro/)).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByTitle(/Boot iPhone 15 Pro/));

    await waitFor(() =>
      expect(vi.mocked(sidecar.mobileSimulatorBoot)).toHaveBeenCalledWith(
        "00001111-AAAA-BBBB-CCCC-000011112222",
      ),
    );
  });

  it("renders empty state when device list is empty", async () => {
    vi.mocked(sidecar.mobileDevices).mockResolvedValue({ devices: [] });
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByText(/Žádná zařízení/i)).toBeInTheDocument(),
    );
  });
});

// ---------------------------------------------------------------------------
// Appium server
// ---------------------------------------------------------------------------

describe("MobilePanel — Appium", () => {
  it("shows Spustit button when Appium is stopped", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Spustit/i })).toBeInTheDocument(),
    );
  });

  it("calls mobileAppiumStart when Spustit is clicked", async () => {
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Spustit/i })).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByRole("button", { name: /Spustit/i }));

    await waitFor(() =>
      expect(vi.mocked(sidecar.mobileAppiumStart)).toHaveBeenCalledOnce(),
    );
  });

  it("shows Zastavit button when Appium is running", async () => {
    vi.mocked(sidecar.mobileAppiumStatus).mockResolvedValue(mockAppiumRunning);
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Zastavit/i })).toBeInTheDocument(),
    );
    expect(screen.getByText(/port 4723/i)).toBeInTheDocument();
  });

  it("calls mobileAppiumStop when Zastavit is clicked", async () => {
    vi.mocked(sidecar.mobileAppiumStatus).mockResolvedValue(mockAppiumRunning);
    await act(async () => {
      render(<MobilePanel />);
    });
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Zastavit/i })).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByRole("button", { name: /Zastavit/i }));

    await waitFor(() =>
      expect(vi.mocked(sidecar.mobileAppiumStop)).toHaveBeenCalledOnce(),
    );
  });
});
