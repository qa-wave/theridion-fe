import { useI18n } from "../lib/i18n/context";
import type { Locale } from "../lib/i18n/types";
import { SUPPORTED_LOCALES } from "../lib/i18n/types";

export function LangSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <div
      role="group"
      aria-label={t("lang.switcher.aria")}
      className="flex items-center gap-0.5"
    >
      {SUPPORTED_LOCALES.map((lang: Locale, i) => (
        <button
          key={lang}
          type="button"
          onClick={() => setLocale(lang)}
          aria-pressed={locale === lang}
          className={`px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
            i < SUPPORTED_LOCALES.length - 1
              ? "border-r border-white/[0.1]"
              : ""
          } ${
            locale === lang
              ? "text-neutral-100"
              : "text-neutral-600 hover:text-neutral-400"
          }`}
        >
          {t(`lang.${lang}` as `lang.en` | `lang.cs`)}
        </button>
      ))}
    </div>
  );
}
