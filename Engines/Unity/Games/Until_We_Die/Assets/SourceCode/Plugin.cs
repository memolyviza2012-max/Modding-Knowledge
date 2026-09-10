using System;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using Il2CppInterop.Runtime;
using Il2CppInterop.Runtime.InteropTypes.Arrays;
using Il2CppInterop.Runtime.Injection;
using UnityEngine;
using UnityEngine.TextCore.LowLevel;
using TMPro;

namespace ThaiFontFallback
{
    [BepInPlugin("th.font.fallback", "Thai Font Fallback", "2.0.0")]
    public class Plugin : BasePlugin
    {
        internal static ManualLogSource _log;
        internal static bool Applied;
        // Resolve relative to the BepInEx root so the mod is portable to any install path.
        static readonly string LogFile = System.IO.Path.Combine(Paths.BepInExRootPath, "ThaiFontFallback.log");
        static readonly string InjectFile = System.IO.Path.Combine(Paths.BepInExRootPath, "th_inject.txt");

        // The placeholder font name we tag; LoadFontFace(Font) is redirected to the TTF path for it.
        internal const string ThaiFontName = "ThaiFallback";
        internal static string ThaiTtfPath;

        internal static class L
        {
            public static void LogInfo(string s) { W("INFO", s); }
            public static void LogWarning(string s) { W("WARN", s); }
            public static void LogError(string s) { W("ERR ", s); }
            static void W(string lvl, string s)
            {
                try { _log?.LogInfo(s); } catch { }
                try { System.IO.File.AppendAllText(LogFile, DateTime.Now.ToString("HH:mm:ss") + " [" + lvl + "] " + s + "\n"); } catch { }
            }
        }

        public override void Load()
        {
            _log = Log;
            try { System.IO.File.WriteAllText(LogFile, "=== ThaiFont v2.0 " + DateTime.Now + " ===\n"); } catch { }

            // pick an installed Thai-capable TTF
            string[] cands = {
                @"C:\Windows\Fonts\leelawui.ttf",   // Leelawadee UI
                @"C:\Windows\Fonts\tahoma.ttf",     // Tahoma (has Thai)
                @"C:\Windows\Fonts\upcjl.ttf"
            };
            foreach (var c in cands) { if (System.IO.File.Exists(c)) { ThaiTtfPath = c; break; } }
            L.LogInfo("[ThaiFont] ttf path = " + (ThaiTtfPath ?? "NONE"));

            var h = new Harmony("th.font.fallback");

            // Redirect FontEngine.LoadFontFace(Font,...) to load our TTF from disk when it's our font.
            PatchLFF(h, new Type[] { typeof(Font), typeof(int) }, nameof(LFF_Font_Int));
            PatchLFF(h, new Type[] { typeof(Font) }, nameof(LFF_Font));

            // Apply the fallback once TMP text appears.
            TryPatch(h, typeof(TMPro.TextMeshProUGUI), "OnEnable");
            TryPatch(h, typeof(TMPro.TextMeshPro), "OnEnable");

            // Trigger I2 Thai injection once localization is actually running (sources loaded).
            TryPatchPostfix(h, typeof(I2.Loc.LocalizationManager), "LocalizeAll", new Type[] { typeof(bool) }, nameof(I2Trigger));
            TryPatchPostfix(h, typeof(I2.Loc.LocalizationManager), "UpdateSources", Type.EmptyTypes, nameof(I2Trigger));

            // On-screen credit watermark (visible from the main menu onward).
            try
            {
                ClassInjector.RegisterTypeInIl2Cpp<CreditOverlay>();
                var go = new GameObject("ThaiModCredit");
                UnityEngine.Object.DontDestroyOnLoad(go);
                go.hideFlags = HideFlags.HideAndDontSave;
                go.AddComponent<CreditOverlay>();
                L.LogInfo("[ThaiFont] credit overlay spawned");
            }
            catch (Exception ce) { L.LogError("[ThaiFont] credit overlay err: " + ce); }

            L.LogInfo("[ThaiFont] Load() done");
        }

        static void PatchLFF(Harmony h, Type[] sig, string prefixName)
        {
            try
            {
                var m = AccessTools.Method(typeof(FontEngine), "LoadFontFace", sig);
                if (m == null) { L.LogWarning("[ThaiFont] LoadFontFace overload not found"); return; }
                var pre = new HarmonyMethod(typeof(Plugin).GetMethod(prefixName, System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic));
                h.Patch(m, prefix: pre);
                L.LogInfo("[ThaiFont] patched FontEngine.LoadFontFace(" + string.Join(",", System.Array.ConvertAll(sig, t => t.Name)) + ")");
            }
            catch (Exception e) { L.LogError("[ThaiFont] PatchLFF err: " + e.Message); }
        }

        // Prefix returns false to skip original when handled.
        static bool LFF_Font_Int(Font font, int pointSize, ref FontEngineError __result)
        {
            if (font != null && font.name == ThaiFontName && ThaiTtfPath != null)
            {
                __result = FontEngine.LoadFontFace(ThaiTtfPath, pointSize);
                return false;
            }
            return true;
        }

        static bool LFF_Font(Font font, ref FontEngineError __result)
        {
            if (font != null && font.name == ThaiFontName && ThaiTtfPath != null)
            {
                __result = FontEngine.LoadFontFace(ThaiTtfPath);
                return false;
            }
            return true;
        }

        static void TryPatch(Harmony h, Type t, string method)
        {
            try
            {
                var m = AccessTools.Method(t, method);
                if (m == null) { L.LogWarning("[ThaiFont] no method " + t.Name + "." + method); return; }
                var post = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(Hook), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic));
                h.Patch(m, postfix: post);
                L.LogInfo("[ThaiFont] patched " + t.Name + "." + method);
            }
            catch (Exception e) { L.LogError("[ThaiFont] patch fail " + t.Name + ": " + e.Message); }
        }

        static void TryPatchPostfix(Harmony h, Type t, string method, Type[] sig, string postName)
        {
            try
            {
                var m = (sig == null || sig.Length == 0) ? AccessTools.Method(t, method) : AccessTools.Method(t, method, sig);
                if (m == null) { L.LogWarning("[ThaiFont] no method " + t.Name + "." + method); return; }
                var post = new HarmonyMethod(typeof(Plugin).GetMethod(postName, System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic));
                h.Patch(m, postfix: post);
                L.LogInfo("[ThaiFont] patched " + t.Name + "." + method);
            }
            catch (Exception e) { L.LogError("[ThaiFont] patch fail " + t.Name + "." + method + ": " + e.Message); }
        }

        static bool _i2running;
        static void I2Trigger()
        {
            if (_i2done || _i2running) return;
            _i2running = true;
            try { InjectI2(); }
            catch (Exception de) { L.LogError("[ThaiFont] InjectI2 err: " + de); }
            finally { _i2running = false; }
        }

        // Re-assert Thai periodically during early game to fix UI built before injection (timing race).
        static float _lastReassert;
        static int _reassertN;
        static void Hook()
        {
            if (!Applied) ApplyFont();

            if (_i2done && _reassertN < 25)
            {
                float t = Time.realtimeSinceStartup;
                if (t - _lastReassert >= 1.0f)
                {
                    _lastReassert = t;
                    _reassertN++;
                    try
                    {
                        if (I2.Loc.LocalizationManager.CurrentLanguage != "Thai")
                            I2.Loc.LocalizationManager.SetLanguageAndCode("Thai", "th", true, true);
                        I2.Loc.LocalizationManager.LocalizeAll(true);
                    }
                    catch { }
                }
            }
        }

        static void ApplyFont()
        {
            Applied = true;
            try
            {
                if (ThaiTtfPath == null) { L.LogError("[ThaiFont] no ttf available"); return; }

                // Placeholder Font tagged with our name; LoadFontFace(Font) is redirected for it.
                var osFont = new Font(ThaiFontName);
                osFont.name = ThaiFontName;

                TMP_FontAsset fa = null;
                try { fa = TMP_FontAsset.CreateFontAsset(osFont, 90, 9, GlyphRenderMode.SDFAA, 1024, 1024, AtlasPopulationMode.Dynamic, true); }
                catch (Exception ce) { L.LogWarning("[ThaiFont] CreateFontAsset(full) err: " + ce.Message); }
                if (fa == null)
                {
                    try { fa = TMP_FontAsset.CreateFontAsset(osFont); }
                    catch (Exception ce2) { L.LogWarning("[ThaiFont] CreateFontAsset(conv) err: " + ce2.Message); }
                }
                if (fa == null) { L.LogError("[ThaiFont] CreateFontAsset returned null"); return; }

                fa.name = "ThaiFallback SDF";
                UnityEngine.Object.DontDestroyOnLoad(fa);
                L.LogInfo("[ThaiFont] CreateFontAsset OK, face=" + fa.faceInfo.familyName);

                // pre-add Thai block
                try
                {
                    var sb = new System.Text.StringBuilder();
                    for (int c = 0x0E00; c <= 0x0E7F; c++) sb.Append((char)c);
                    bool added = fa.TryAddCharacters(sb.ToString(), false);
                    L.LogInfo("[ThaiFont] TryAddCharacters(Thai) = " + added + ", chars=" + fa.characterTable.Count);
                }
                catch (Exception ae) { L.LogWarning("[ThaiFont] TryAddCharacters err: " + ae.Message); }

                bool hasThai = false;
                try { hasThai = fa.HasCharacter((int)'ก'); } catch { }
                L.LogInfo("[ThaiFont] HasThaiGlyph(ก) = " + hasThai);

                var fb = TMP_Settings.fallbackFontAssets;
                if (fb == null) { fb = new Il2CppSystem.Collections.Generic.List<TMP_FontAsset>(); L.LogWarning("[ThaiFont] new fallback list"); }
                fb.Add(fa);
                L.LogInfo("[ThaiFont] added to global fallback, count=" + fb.Count + " -- DONE");
            }
            catch (Exception e) { L.LogError("[ThaiFont] ApplyFont err: " + e); }
        }

        static bool _i2done;
        static void InjectI2()
        {
            if (_i2done) return;
            string file = InjectFile;
            if (!System.IO.File.Exists(file)) { L.LogWarning("[ThaiFont] th_inject.txt missing"); return; }

            var sources = I2.Loc.LocalizationManager.Sources;
            if (sources == null || sources.Count == 0) { L.LogWarning("[ThaiFont] no I2 sources yet"); return; }
            L.LogInfo("[ThaiFont] I2 sources = " + sources.Count);

            // add Thai language to each source
            for (int s = 0; s < sources.Count; s++)
            {
                var src = sources[s];
                if (src.GetLanguageIndex("Thai", true, false) < 0)
                    src.AddLanguage("Thai", "th");
            }

            var lines = System.IO.File.ReadAllLines(file);
            int applied = 0, missing = 0;
            foreach (var raw in lines)
            {
                if (string.IsNullOrEmpty(raw)) continue;
                int tab = raw.IndexOf('\t');
                if (tab < 0) continue;
                string term = raw.Substring(0, tab);
                string thai = raw.Substring(tab + 1).Replace("\\n", "\n");
                if (thai.Length == 0) continue;

                bool found = false;
                for (int s = 0; s < sources.Count; s++)
                {
                    var src = sources[s];
                    var td = src.GetTermData(term, false);
                    if (td != null)
                    {
                        int idx = src.GetLanguageIndex("Thai", true, false);
                        td.SetTranslation(idx, thai, null);
                        found = true;
                        break;
                    }
                }
                if (found) applied++; else missing++;
            }
            for (int s = 0; s < sources.Count; s++) sources[s].UpdateDictionary(true);
            L.LogInfo("[ThaiFont] I2 inject applied=" + applied + " missing=" + missing);

            try { I2.Loc.LocalizationManager.SetLanguageAndCode("Thai", "th", true, true); }
            catch (Exception se) { L.LogWarning("[ThaiFont] SetLanguage err: " + se.Message); }
            try { I2.Loc.LocalizationManager.LocalizeAll(true); } catch { }
            L.LogInfo("[ThaiFont] current language = " + I2.Loc.LocalizationManager.CurrentLanguage);
            _i2done = true;
        }

        static void DumpI2()
        {
            string outPath = System.IO.Path.Combine(Paths.BepInExRootPath, "i2_terms.txt");
            var terms = I2.Loc.LocalizationManager.GetTermsList("");
            if (terms == null) { L.LogWarning("[ThaiFont] I2 terms null"); return; }
            L.LogInfo("[ThaiFont] I2 term count = " + terms.Count);
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < terms.Count; i++)
            {
                string term = terms[i];
                string eng = "";
                try { eng = I2.Loc.LocalizationManager.GetTranslation(term, false, 0, false, false, null, "English"); }
                catch { }
                if (eng == null) eng = "";
                sb.Append(term).Append("\t").Append(eng.Replace("\r", "").Replace("\n", "\\n")).Append("\n");
            }
            System.IO.File.WriteAllText(outPath, sb.ToString());
            L.LogInfo("[ThaiFont] I2 dump written: " + outPath + " (" + terms.Count + " terms)");
        }
    }

    // Small persistent credit drawn in the bottom-left corner via IMGUI.
    // Uses a dynamic OS font so Thai renders correctly in IMGUI.
    public class CreditOverlay : MonoBehaviour
    {
        public CreditOverlay(IntPtr ptr) : base(ptr) { }

        const string CreditText = "ม็อดภาษาไทย  BY LUNG DEAR";
        const int FontSize = 15;

        static bool _init;
        static Font _font;
        static GUIStyle _style;
        static GUIStyle _shadow;

        void OnGUI()
        {
            if (!_init)
            {
                _init = true;
                try
                {
                    _font = Font.CreateDynamicFontFromOSFont("Leelawadee UI", FontSize);
                    if (_font == null) _font = Font.CreateDynamicFontFromOSFont("Tahoma", FontSize);
                    if (_font != null) UnityEngine.Object.DontDestroyOnLoad(_font);
                }
                catch { }

                _shadow = new GUIStyle();
                _shadow.fontSize = FontSize;
                if (_font != null) _shadow.font = _font;
                _shadow.normal.textColor = new Color(0f, 0f, 0f, 0.6f);

                _style = new GUIStyle();
                _style.fontSize = FontSize;
                if (_font != null) _style.font = _font;
                _style.normal.textColor = new Color(0.43f, 0.89f, 0.55f, 0.85f); // soft green
            }

            const float w = 320f, h = 22f, pad = 10f;
            float x = pad;
            float y = Screen.height - h - pad;
            GUI.Label(new Rect(x + 1f, y + 1f, w, h), CreditText, _shadow);
            GUI.Label(new Rect(x, y, w, h), CreditText, _style);
        }
    }
}
