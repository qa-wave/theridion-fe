/**
 * Mobile — Native mobile device management sidecar client.
 *
 * Wraps /api/mobile/* endpoints (tooling, devices, simulator/emulator boot,
 * Appium server lifecycle).
 */

import { call } from "./client";

// ---- Types ----------------------------------------------------------------

export interface MobileTool {
  name: string;
  available: boolean;
  path: string | null;
}

export interface MobileToolingOutput {
  tools: MobileTool[];
}

export interface MobileDevice {
  id: string;
  name: string;
  platform: "android" | "ios";
  state: string;
}

export interface MobileDevicesOutput {
  devices: MobileDevice[];
}

export interface MobileMessageOutput {
  message: string;
}

export interface AppiumStartOutput {
  port: number;
  pid: number;
  message: string;
}

export interface AppiumStatusOutput {
  running: boolean;
  port: number;
  detail?: string;
}

// ---- Methods ----------------------------------------------------------------

export const mobileMethods = {
  /** Check availability of local mobile tooling (adb, xcrun, appium, emulator). */
  mobileTooling(): Promise<MobileToolingOutput> {
    return call<MobileToolingOutput>("/api/mobile/tooling");
  },

  /** List connected/booted Android emulators and iOS simulators. */
  mobileDevices(): Promise<MobileDevicesOutput> {
    return call<MobileDevicesOutput>("/api/mobile/devices");
  },

  /** Boot an iOS simulator by UDID (macOS only). */
  mobileSimulatorBoot(udid: string): Promise<MobileMessageOutput> {
    return call<MobileMessageOutput>("/api/mobile/simulator/boot", {
      method: "POST",
      body: JSON.stringify({ udid }),
    });
  },

  /** Start an Android emulator by AVD name. */
  mobileEmulatorStart(avd: string): Promise<MobileMessageOutput> {
    return call<MobileMessageOutput>("/api/mobile/emulator/start", {
      method: "POST",
      body: JSON.stringify({ avd }),
    });
  },

  /** Start Appium server on the given port (default 4723). */
  mobileAppiumStart(port?: number): Promise<AppiumStartOutput> {
    return call<AppiumStartOutput>("/api/mobile/appium/start", {
      method: "POST",
      body: JSON.stringify(port !== undefined ? { port } : {}),
    });
  },

  /** Stop Appium server on the given port (default 4723). */
  mobileAppiumStop(port?: number): Promise<MobileMessageOutput> {
    return call<MobileMessageOutput>("/api/mobile/appium/stop", {
      method: "POST",
      body: JSON.stringify(port !== undefined ? { port } : {}),
    });
  },

  /** Check whether Appium is running on the given port (default 4723). */
  mobileAppiumStatus(port?: number): Promise<AppiumStatusOutput> {
    const qs = port !== undefined ? `?port=${port}` : "";
    return call<AppiumStatusOutput>(`/api/mobile/appium/status${qs}`);
  },
};
