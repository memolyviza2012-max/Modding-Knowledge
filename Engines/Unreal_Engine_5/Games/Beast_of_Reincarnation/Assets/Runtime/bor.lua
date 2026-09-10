local WIN_P = '44 39 ?? 08 74 16 48 8B 08 48 85 C9 74 0E 48 8B 01 FF 50 30 84 C0 74 04 B0 01 EB 02 32 C0 88'
local WIN_U = '48 8B 5D 88 4C 8B 65 C0 0F AF 46 28 0F B6 7E 50 44 8B E8 4D 03 EC E8 ?? ?? ?? ?? 44 39 70 08'
local LIN_P = ''
local LIN_U = ''

local getByteLen = function(pattern)
  return math.floor(pattern:gsub(' ', ''):len()/2)
end

local getOS = function()
  return package.config:sub(1,1) == "\\" and "win" or "unix"
end

local get_p = function()
  local result = LIN_P
  if (getOS() == "win") then
    result = WIN_P
  end
  return result
end

local get_u = function()
  local result = LIN_U
  if (getOS() == "win") then
    result = WIN_U
  end
  return result
end

local patch_u = function(ctx)
  local OS = getOS()
  print(string.format("PatchU for %s: [%s] (%d)", OS, get_u(), getByteLen(WIN_U)))
  if (OS == "win") then
    ctx[ctx:address() + getByteLen(WIN_U)] = 0x75
  else
    ctx[ctx:address() + getByteLen(LIN_U)] = 0xEB
  end
end

local patch_p = function(ctx)
  local OS = getOS()
  print(string.format("PatchP for %s: [%s]", OS, get_p()))
  if (OS == "win") then
      local len = getByteLen(WIN_P) - 1
      ctx[ctx:address() + (len+0)] = 0x90
      ctx[ctx:address() + (len+1)] = 0x90
      ctx[ctx:address() + (len+2)] = 0x90
  else
      local len = getByteLen(LIN_P)
      ctx[ctx:address() + (len+0)] = 0x90
      ctx[ctx:address() + (len+1)] = 0x90
      ctx[ctx:address() + (len+2)] = 0x90
      ctx[ctx:address() + (len+3)] = 0x90
  end
end

return
{
  { pattern = tostring(get_p()), match = patch_p },
  { pattern = tostring(get_u()), match = patch_u },
}