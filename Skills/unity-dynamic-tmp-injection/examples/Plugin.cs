using System;
using System.IO;
using System.Reflection;
using BepInEx;
using UnityEngine;
using TMPro;

namespace DynamicFontInjector
{
    [BepInPlugin("com.modder.dynamicfontinjector", "Dynamic TMP Font Injector", "1.0.0")]
    public class FontInjectorPlugin : BaseUnityPlugin
    {
        private void Awake()
        {
            Logger.LogInfo("Dynamic Font Injector is starting...");
            try
            {
                // 1. Get the path to the .ttf file (assumed to be in the same folder as this DLL)
                string pluginDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                string fontPath = Path.Combine(pluginDir, "custom_font.ttf");
                
                if (!File.Exists(fontPath))
                {
                    Logger.LogError("Could not find custom_font.ttf in " + pluginDir);
                    return;
                }
                
                // 2. Load the raw TTF file as a standard Unity Font
                Font osFont = new Font(fontPath);
                
                // 3. Dynamically generate a TMP_FontAsset
                TMP_FontAsset dynamicFontAsset = TMP_FontAsset.CreateFontAsset(osFont);
                dynamicFontAsset.name = "DynamicFont_TMP";
                
                // 4. Ensure it persists across scene loads
                DontDestroyOnLoad(dynamicFontAsset);
                
                // 5. Inject into the TMP Global Fallback List
                if (TMP_Settings.fallbackFontAssets != null)
                {
                    TMP_Settings.fallbackFontAssets.Add(dynamicFontAsset);
                    Logger.LogInfo("SUCCESS: Injected DynamicFont_TMP into TMP_Settings global fallback list!");
                }
                else
                {
                    Logger.LogWarning("TMP_Settings.fallbackFontAssets is null! Cannot inject globally.");
                }
            }
            catch (Exception ex)
            {
                Logger.LogError("Failed to inject Dynamic Font: " + ex.Message);
            }
        }
    }
}
