# copied from https://github.com/MAVENSDC/PyTplot/blob/master/pytplot/spedas_colorbar.py

r = [0,
   2,
   4,
   7,
  11,
  14,
  17,
  20,
  24,
  27,
  30,
  34,
  38,
  42,
  47,
  52,
  62,
  72,
  74,
  75,
  77,
  78,
  79,
  81,
  82,
  83,
  84,
  84,
  85,
  85,
  85,
  85,
  85,
  81,
  77,
  74,
  69,
  68,
  66,
  65,
  62,
  60,
  58,
  55,
  53,
  50,
  46,
  43,
  39,
  29,
  18,
  11,
   6,
   2,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   1,
   4,
  16,
  34,
  50,
  64,
  75,
  81,
  90,
 107,
 123,
 123,
 123,
 131,
 141,
 141,
 149,
 160,
 169,
 176,
 181,
 181,
 182,
 187,
 191,
 197,
 202,
 211,
 221,
 228,
 235,
 238,
 241,
 243,
 246,
 248,
 249,
 250,
 251,
 253,
 253,
 254,
 254,
 254,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 254,
 254,
 253,
 252,
 251,
 248,
 246,
 242,
 238,
 231,
 224,
 218,
 212,
 206,
 201,
 197,
 192,
 189,
 185,
 182,
 179,
 176,
 173,
 170,
 167]

g = [0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   2,
   6,
  11,
  17,
  22,
  28,
  32,
  37,
  41,
  46,
  50,
  55,
  59,
  70,
  82,
  90,
  97,
 102,
 109,
 114,
 118,
 124,
 130,
 137,
 144,
 150,
 157,
 163,
 168,
 177,
 188,
 196,
 202,
 208,
 212,
 217,
 222,
 226,
 231,
 235,
 239,
 243,
 246,
 249,
 251,
 252,
 253,
 254,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 254,
 253,
 252,
 250,
 249,
 246,
 244,
 242,
 240,
 239,
 238,
 237,
 237,
 235,
 234,
 231,
 226,
 218,
 212,
 205,
 199,
 196,
 192,
 186,
 180,
 174,
 167,
 163,
 159,
 155,
 150,
 145,
 139,
 132,
 123,
 116,
 112,
 110,
 110,
 109,
 107,
 106,
 103,
 101,
  95,
  88,
  78,
  67,
  63,
  63,
  58,
  48,
  33,
  27,
  16,
   5,
   3,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0]

b = [0,
   1,
   2,
   5,
   9,
  11,
  14,
  16,
  20,
  23,
  26,
  30,
  35,
  40,
  46,
  52,
  68,
  84,
  90,
  95,
  98,
 101,
 104,
 108,
 112,
 117,
 121,
 125,
 128,
 132,
 135,
 138,
 141,
 158,
 174,
 181,
 190,
 194,
 197,
 201,
 204,
 208,
 212,
 215,
 219,
 223,
 228,
 232,
 236,
 242,
 249,
 251,
 252,
 253,
 253,
 254,
 254,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 255,
 254,
 253,
 253,
 250,
 247,
 243,
 238,
 227,
 212,
 202,
 196,
 191,
 187,
 183,
 178,
 167,
 161,
 156,
 150,
 146,
 142,
 137,
 133,
 124,
 111,
 100,
  91,
  84,
  78,
  72,
  67,
  62,
  58,
  53,
  47,
  42,
  28,
  13,
   5,
   1,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0]
