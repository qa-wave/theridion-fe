/**
 * MobilePanel — Native mobile device management panel.
 *
 * Sections:
 *   (a) Tooling availability — adb / xcrun / appium / emulator with green/red dots
 *   (b) Device list — connected Android emulators + iOS simulators with Boot/Start actions
 *   (c) Appium server control — Start/Stop + live status
 *
 * Matches SilkPanel visual style: neutral-925 surfaces, emerald accents,
 * lucide-react icons, text-xs. Czech UI copy.
 */

import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Cpu,
  RefreshCw,
  Server,
  Smartphone,
  XCircle,
  Zap,
} from "lucide-react";
import { EmptyState } from "./EmptyState";
import { sidecar } from "../lib/sidecar";
import { useT } from "../lib/i18n/context";
import type {
  AppiumStatusOutput,
  MobileDevice,
  MobileTool,
} from "../lib/sidecar/mobile";

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Small availability dot (green = available, red = missing). */
function AvailabilityDot({ available }: { available: boolean }) {
  const t = useT();
  return (
    <span
      className={`inline-block h-2 w-2 rounded-full shrink-0 ${
        available ? "bg-emerald-400" : "bg-red-500"
      }`}
      aria-label={available ? t("mobile.tooling.dot.available") : t("mobile.tooling.dot.unavailable")}
    />
  );
}

/** Platform badge: iOS (blue) or Android (green). */
function PlatformBadge({ platform }: { platform: "android" | "ios" }) {
  return (
    <span
      className={`rounded border px-1.5 py-0.5 text-[9px] font-medium uppercase shrink-0 ${
        platform === "ios"
          ? "border-blue-800 bg-blue-950/50 text-blue-300"
          : "border-emerald-800 bg-emerald-950/50 text-emerald-300"
      }`}
    >
      {platform === "ios" ? "iOS" : "Android"}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Tooling section
// ---------------------------------------------------------------------------

function ToolingSection({ tools, loading }: { tools: MobileTool[]; loading: boolean }) {
  const t = useT();
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-3 flex flex-col gap-2">
      <h3 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
        <Cpu size={12} className="text-neutral-500" />
        {t("mobile.tooling.title")}
      </h3>
      {loading ? (
        <div className="flex items-center gap-1.5 text-xs text-neutral-500">
          <RefreshCw size={11} className="animate-spin" />
          {t("mobile.tooling.loading")}
        </div>
      ) : tools.length === 0 ? (
        <div className="text-xs text-neutral-600">{t("mobile.tooling.empty")}</div>
      ) : (
        <ul className="flex flex-col gap-1.5">
          {tools.map((tool) => (
            <li key={tool.name} className="flex items-center gap-2">
              <AvailabilityDot available={tool.available} />
              <span className="font-mono text-xs text-neutral-300 w-20 shrink-0">{tool.name}</span>
              {tool.path ? (
                <span className="text-[10px] text-neutral-600 truncate font-mono">{tool.path}</span>
              ) : (
                <span className="text-[10px] text-neutral-700 italic">{t("mobile.tooling.notFound")}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Device list section
// ---------------------------------------------------------------------------

interface DeviceRowProps {
  device: MobileDevice;
  onBoot: (device: MobileDevice) => void;
  booting: boolean;
}

function DeviceRow({ device, onBoot, booting }: DeviceRowProps) {
  const t = useT();
  const isRunning =
    device.state.toLowerCase() === "booted" ||
    device.state.toLowerCase() === "online" ||
    device.state.toLowerCase() === "running";

  const actionLabel = device.platform === "ios" ? t("mobile.devices.action.boot") : t("mobile.devices.action.start");

  return (
    <div className="flex items-center gap-2 rounded border border-neutral-800 bg-neutral-950 px-3 py-2">
      <PlatformBadge platform={device.platform} />
      <div className="flex-1 min-w-0">
        <div className="text-xs text-neutral-200 truncate">{device.name}</div>
        <div className="text-[10px] text-neutral-600 font-mono truncate">{device.id}</div>
      </div>
      <span
        className={`text-[10px] shrink-0 ${
          isRunning ? "text-emerald-400" : "text-neutral-600"
        }`}
      >
        {device.state}
      </span>
      {!isRunning && (
        <button
          onClick={() => onBoot(device)}
          disabled={booting}
          className="flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-medium bg-neutral-800 hover:bg-neutral-700 disabled:opacity-40 text-neutral-200 transition-colors shrink-0"
          title={`${actionLabel} ${device.name}`}
        >
          {booting ? <RefreshCw size={9} className="animate-spin" /> : <Zap size={9} />}
          {actionLabel}
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Appium section
// ---------------------------------------------------------------------------

interface AppiumSectionProps {
  status: AppiumStatusOutput | null;
  loading: boolean;
  onStart: () => void;
  onStop: () => void;
  acting: boolean;
}

function AppiumSection({ status, loading, onStart, onStop, acting }: AppiumSectionProps) {
  const t = useT();
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-3 flex flex-col gap-2">
      <h3 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
        <Server size={12} className="text-neutral-500" />
        {t("mobile.appium.title")}
      </h3>

      {loading ? (
        <div className="flex items-center gap-1.5 text-xs text-neutral-500">
          <RefreshCw size={11} className="animate-spin" />
          {t("mobile.appium.loading")}
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {status?.running ? (
              <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
            ) : (
              <XCircle size={13} className="text-neutral-600 shrink-0" />
            )}
            <span className="text-xs text-neutral-300">
              {status?.running
                ? t("mobile.appium.running", { port: status.port })
                : t("mobile.appium.stopped")}
            </span>
            {status?.detail && (
              <span className="text-[10px] text-neutral-600 truncate max-w-[160px]">
                {status.detail}
              </span>
            )}
          </div>
          {status?.running ? (
            <button
              onClick={onStop}
              disabled={acting}
              data-testid="appium-stop-btn"
              className="flex items-center gap-1 rounded px-2.5 py-1 text-xs font-medium bg-red-900/60 hover:bg-red-800/60 disabled:opacity-40 text-red-300 border border-red-800 transition-colors shrink-0"
            >
              {acting ? <RefreshCw size={10} className="animate-spin" /> : <XCircle size={10} />}
              {t("mobile.appium.stop")}
            </button>
          ) : (
            <button
              onClick={onStart}
              disabled={acting}
              data-testid="appium-start-btn"
              className="flex items-center gap-1 rounded px-2.5 py-1 text-xs font-medium bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white transition-colors shrink-0"
            >
              {acting ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />}
              {t("mobile.appium.start")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main MobilePanel
// ---------------------------------------------------------------------------

interface MobilePanelProps {
  onToast?: (type: "success" | "error" | "info", message: string) => void;
}

export function MobilePanel({ onToast }: MobilePanelProps) {
  const t = useT();
  const [tools, setTools] = useState<MobileTool[]>([]);
  const [loadingTools, setLoadingTools] = useState(false);

  const [devices, setDevices] = useState<MobileDevice[]>([]);
  const [loadingDevices, setLoadingDevices] = useState(false);
  const [devicesError, setDevicesError] = useState<string | null>(null);
  const [bootingId, setBootingId] = useState<string | null>(null);

  const [appiumStatus, setAppiumStatus] = useState<AppiumStatusOutput | null>(null);
  const [loadingAppium, setLoadingAppium] = useState(false);
  const [appiumActing, setAppiumActing] = useState(false);

  // Load tooling on mount
  useEffect(() => {
    setLoadingTools(true);
    sidecar
      .mobileTooling()
      .then((res) => setTools(res.tools))
      .catch(() => {
        // Non-blocking — tooling list optional
      })
      .finally(() => setLoadingTools(false));
  }, []);

  // Load devices + appium status on mount
  const refreshDevices = useCallback(async () => {
    setLoadingDevices(true);
    setDevicesError(null);
    try {
      const res = await sidecar.mobileDevices();
      setDevices(res.devices);
    } catch (e: unknown) {
      setDevicesError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingDevices(false);
    }
  }, []);

  const refreshAppiumStatus = useCallback(async () => {
    setLoadingAppium(true);
    try {
      const res = await sidecar.mobileAppiumStatus();
      setAppiumStatus(res);
    } catch {
      // Non-blocking — show as unknown/stopped
    } finally {
      setLoadingAppium(false);
    }
  }, []);

  useEffect(() => {
    void refreshDevices();
    void refreshAppiumStatus();
  }, [refreshDevices, refreshAppiumStatus]);

  const handleBoot = useCallback(
    async (device: MobileDevice) => {
      setBootingId(device.id);
      try {
        if (device.platform === "ios") {
          await sidecar.mobileSimulatorBoot(device.id);
          onToast?.("success", `Simulator ${device.name} se spouští.`);
        } else {
          await sidecar.mobileEmulatorStart(device.name);
          onToast?.("success", `Emulator ${device.name} se spouští.`);
        }
        // Refresh list to reflect updated state
        await refreshDevices();
      } catch (e: unknown) {
        onToast?.(
          "error",
          `Chyba: ${e instanceof Error ? e.message : String(e)}`,
        );
      } finally {
        setBootingId(null);
      }
    },
    [onToast, refreshDevices],
  );

  const handleAppiumStart = useCallback(async () => {
    setAppiumActing(true);
    try {
      const res = await sidecar.mobileAppiumStart();
      onToast?.("success", `Appium spuštěn na portu ${res.port}.`);
      await refreshAppiumStatus();
    } catch (e: unknown) {
      onToast?.(
        "error",
        `Appium start selhal: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setAppiumActing(false);
    }
  }, [onToast, refreshAppiumStatus]);

  const handleAppiumStop = useCallback(async () => {
    setAppiumActing(true);
    try {
      await sidecar.mobileAppiumStop();
      onToast?.("info", "Appium zastaven.");
      await refreshAppiumStatus();
    } catch (e: unknown) {
      onToast?.(
        "error",
        `Appium stop selhal: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setAppiumActing(false);
    }
  }, [onToast, refreshAppiumStatus]);

  return (
    <div className="flex h-full flex-col bg-neutral-950 text-neutral-200 overflow-y-auto">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-neutral-800 px-3 py-2 shrink-0">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-neutral-300">
          <Smartphone size={13} className="text-emerald-500" />
          {t("mobile.title")}
        </div>
        <button
          onClick={() => void refreshDevices()}
          disabled={loadingDevices}
          title={t("mobile.refresh.title")}
          className="flex items-center gap-1 text-xs text-neutral-500 hover:text-neutral-300 transition-colors"
        >
          <RefreshCw size={12} className={loadingDevices ? "animate-spin" : ""} />
          {t("mobile.refresh")}
        </button>
      </div>

      {/* Content */}
      <div className="flex flex-col gap-4 p-4 flex-1">
        {/* Tooling */}
        <ToolingSection tools={tools} loading={loadingTools} />

        {/* Device list */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
              <Smartphone size={12} className="text-neutral-500" />
              {t("mobile.devices.title")}
            </h3>
            {devicesError && (
              <div className="flex items-center gap-1 text-[10px] text-red-400">
                <AlertCircle size={10} />
                {devicesError}
              </div>
            )}
          </div>

          {loadingDevices ? (
            <div className="flex items-center gap-1.5 text-xs text-neutral-500">
              <RefreshCw size={11} className="animate-spin" />
              {t("mobile.devices.loading")}
            </div>
          ) : devices.length === 0 ? (
            <EmptyState
              icon={Smartphone}
              title={t("mobile.devices.empty.title")}
              description={t("mobile.devices.empty.description")}
            />
          ) : (
            <div className="flex flex-col gap-1.5">
              {devices.map((device) => (
                <DeviceRow
                  key={device.id}
                  device={device}
                  onBoot={handleBoot}
                  booting={bootingId === device.id}
                />
              ))}
            </div>
          )}
        </div>

        {/* Appium server */}
        <AppiumSection
          status={appiumStatus}
          loading={loadingAppium}
          onStart={handleAppiumStart}
          onStop={handleAppiumStop}
          acting={appiumActing}
        />
      </div>
    </div>
  );
}
