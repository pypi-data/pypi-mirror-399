/**
 * Copyright 2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
#define MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_

#include <functional>
#include <any>
#include <unordered_map>
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
enum class OpType {
  kDropoutGenMaskExt = 0,
  kInplaceSubExt = 1,
  kGroupNorm = 2,
  kLessEqual = 3,
  kReflectionPad1DGrad = 4,
  kCountNonZero = 5,
  kLinSpaceExt = 6,
  kReflectionPad1D = 7,
  kBatchNormGradExt = 8,
  kCol2ImGrad = 9,
  kInplaceMatmulAdd = 10,
  kEqual = 11,
  kInplaceSigmoid = 12,
  kLog1p = 13,
  kSoftShrink = 14,
  kSplitTensor = 15,
  kMatMulExt = 16,
  kGatherDGradV2 = 17,
  kReplicationPad3DGrad = 18,
  kMinimum = 19,
  kInplaceErfinv = 20,
  kTraceExt = 21,
  kUpsampleNearest3D = 22,
  kAddRmsNorm = 23,
  kSilentCheckV3 = 24,
  kTanh = 25,
  kFrac = 26,
  kUpsampleLinear1D = 27,
  kCast = 28,
  kInplaceRemainderTensorScalar = 29,
  kSign = 30,
  kMaskedSelect = 31,
  kInplaceClampTensor = 32,
  kInplaceIndexAddExt = 33,
  kMaxDim = 34,
  kAtan2Ext = 35,
  kBitwiseNot = 36,
  kMatMul = 37,
  kGenerator = 38,
  kGLU = 39,
  kInplaceThreshold = 40,
  kSlice = 41,
  kCrossEntropyLossGrad = 42,
  kUpsampleTrilinear3DGrad = 43,
  kAdaptiveMaxPool1D = 44,
  kArgMaxExt = 45,
  kDiagExt = 46,
  kScatter = 47,
  kNarrow = 48,
  kMaskedSelectGrad = 49,
  kInplaceFillScalar = 50,
  kUnique2 = 51,
  kMedianDim = 52,
  kImagView = 53,
  kRmsNorm = 54,
  kRandIntLike = 55,
  kAddmv = 56,
  kBatchNormReduceGrad = 57,
  kFloorDivScalar = 58,
  kDivs = 59,
  kCosh = 60,
  kCellBackwardHook = 61,
  kSwiglu = 62,
  kAdaptiveAvgPool3DGradExt = 63,
  kEluExt = 64,
  kInplaceScatterValueReduce = 65,
  kInplaceReLU = 66,
  kReverseV2 = 67,
  kFlashAttentionScore = 68,
  kConv3DExt = 69,
  kCumminExt = 70,
  kBitwiseOrTensor = 71,
  kReduceMin = 72,
  kSigmoid = 73,
  kTrunc = 74,
  kInplaceMul = 75,
  kAddcmulExt = 76,
  kArgSort = 77,
  kLerp = 78,
  kSqrt = 79,
  kUpsampleBilinear2D = 80,
  kInplaceRemainderTensorTensor = 81,
  kSplitTensorView = 82,
  kInplaceAddsExt = 83,
  kRemainderScalarTensor = 84,
  kPolar = 85,
  kRandn = 86,
  kAvgPool3DGradExt = 87,
  kSliceExtView = 88,
  kSplitWithSize = 89,
  kIsInf = 90,
  kReplicationPad1DGrad = 91,
  kAvgPool2DGrad = 92,
  kSplitWithSizeView = 93,
  kInplaceFloorDivides = 94,
  kIsClose = 95,
  kNLLLoss2d = 96,
  kClampTensor = 97,
  kDiv = 98,
  kReflectionPad2DGrad = 99,
  kMaxPoolGradWithIndices = 100,
  kAcoshExt = 101,
  kSmoothL1LossGrad = 102,
  kGeluGradExt = 103,
  kBatchNormElemtGrad = 104,
  kEmbeddingDenseBackward = 105,
  kReflectionPad3D = 106,
  kMv = 107,
  kReplicationPad1D = 108,
  kInplaceAddmm = 109,
  kIndexSelect = 110,
  kView = 111,
  kInplaceMaskedFillScalar = 112,
  kChunkView = 113,
  kNormalFloatFloat = 114,
  kMoeDistributeCombine = 115,
  kMoeTokenPermuteGrad = 116,
  kNonZeroExt = 117,
  kUpsampleBicubic2D = 118,
  kDequantSwigluQuant = 119,
  kAddExt = 120,
  kHardtanh = 121,
  kBatchNormStats = 122,
  kCeil = 123,
  kInplaceIndexCopy = 124,
  kTransposeExtView = 125,
  kGridSampler3DGrad = 126,
  kSpeedFusionAttention = 127,
  kAcosExt = 128,
  kIm2ColExt = 129,
  kGeluExt = 130,
  kFloorDiv = 131,
  kInplacePut = 132,
  kTransposeView = 133,
  kConv3DPadding = 134,
  kSoftShrinkGrad = 135,
  kSwigluGrad = 136,
  kLogSoftmaxExt = 137,
  kInplaceDivs = 138,
  kLeakyReLUGradExt = 139,
  kRotaryPositionEmbedding = 140,
  kRound = 141,
  kToOther = 142,
  kInplaceHardtanh = 143,
  kThresholdGrad = 144,
  kInplaceBernoulliTensor = 145,
  kInplaceZero = 146,
  kFFNExt = 147,
  kGreaterEqual = 148,
  kSinc = 149,
  kBroadcastTo = 150,
  kLog2 = 151,
  kTriu = 152,
  kCummax = 153,
  kInnerMoeTokenUnpermute = 154,
  kBatchNormElemt = 155,
  kUniqueConsecutive = 156,
  kNeg = 157,
  kReplicationPad3D = 158,
  kTile = 159,
  kConv2DPadding = 160,
  kGeLUGrad = 161,
  kNewZeros = 162,
  kNewFull = 163,
  kCol2ImExt = 164,
  kUniqueDim = 165,
  kAsinExt = 166,
  kSoftmaxBackward = 167,
  kSiLUGrad = 168,
  kPromptFlashAttention = 169,
  kGatherD = 170,
  kDropoutDoMaskExt = 171,
  kReplicationPad2D = 172,
  kSelectV2 = 173,
  kInplaceLog = 174,
  kSoftplusExt = 175,
  kMaskedFillScalar = 176,
  kAdaptiveAvgPool3DExt = 177,
  kInplaceDivMod = 178,
  kKLDiv = 179,
  kNewOnes = 180,
  kGridSampler2DGrad = 181,
  kArgMinWithValue = 182,
  kReplicationPad2DGrad = 183,
  kDot = 184,
  kAdamW = 185,
  kMatmulReduceScatter = 186,
  kNormalTensorTensor = 187,
  kSmoothL1Loss = 188,
  kNorm = 189,
  kLerpScalar = 190,
  kUpsampleBilinear2DGrad = 191,
  kSigmoidGrad = 192,
  kPowScalarTensor = 193,
  kMuls = 194,
  kPReLUGrad = 195,
  kInplaceAddExt = 196,
  kOuter = 197,
  kGridSampler3D = 198,
  kNeScalar = 199,
  kMedianExt = 200,
  kInplaceMaskedScatter = 201,
  kCopy = 202,
  kUpsampleNearest2D = 203,
  kTake = 204,
  kMeshgrid = 205,
  kAllGatherMatmul = 205,
  kMultinomialExt = 206,
  kCustomExt = 207,
  kSoftplusGradExt = 208,
  kBinaryCrossEntropy = 209,
  kNLLLoss = 210,
  kInplaceDivMods = 211,
  kHardtanhGrad = 212,
  kRingAttentionUpdate = 213,
  kIdentity = 214,
  kLinalgVectorNorm = 215,
  kVarMean = 216,
  kScatterValue = 217,
  kBaddbmm = 218,
  kRoll = 219,
  kSinh = 220,
  kPow = 221,
  kIndexFillTensor = 222,
  kTopkExt = 223,
  kEmptyLike = 224,
  kEmbedding = 225,
  kConvolutionStr = 226,
  kConv1DExt = 227,
  kAbs = 228,
  kBinaryCrossEntropyWithLogitsBackward = 229,
  kDivMods = 230,
  kCumsumExt = 231,
  kInnerUnique = 232,
  kInplaceTanh = 233,
  kContiguous = 234,
  kNansum = 235,
  kFmodScalar = 236,
  kL1LossExt = 237,
  kLog = 238,
  kAddLayerNormV2 = 239,
  kMaxPoolWithIndices = 240,
  kInplaceScatterSrcReduce = 241,
  kInplaceIndexFillTensor = 242,
  kUnstackExtView = 243,
  kInplaceGroupedMatmulAdd = 244,
  kErfinv = 245,
  kStdMean = 246,
  kIndex = 247,
  kConvolution = 248,
  kAvgPool1D = 249,
  kReduceMax = 250,
  kLogSoftmaxGrad = 251,
  kInplaceCopy = 252,
  kNarrowView = 253,
  kLogSoftmax = 254,
  kBitwiseOrScalar = 255,
  kSoftmax = 256,
  kExp = 257,
  kKthvalue = 258,
  kBitwiseAndScalar = 259,
  kConstantPadND = 260,
  kAtanh = 261,
  kSoftMarginLoss = 262,
  kInnerInplaceIndexPut = 263,
  kErfc = 264,
  kPReLU = 265,
  kAdaptiveMaxPool2D = 266,
  kReflectionPad3DGrad = 267,
  kTypeAs = 268,
  kStd = 269,
  kLogAddExp = 270,
  kSquare = 271,
  kBatchNormExt = 272,
  kEmpty = 273,
  kErf = 274,
  kInplaceNormal = 275,
  kBroadcastToView = 276,
  kExpandAs = 277,
  kLayerNormGradExt = 277,
  kDropoutExt = 278,
  kSeluGrad = 279,
  kIndexAddExt = 280,
  kNewEmpty = 281,
  kReshape = 282,
  kMaxPoolWithMask = 283,
  kInplaceScatterAdd = 284,
  kXlogy = 285,
  kAsinhExt = 286,
  kIncreFlashAttention = 287,
  kConv2DExt = 288,
  kMin = 289,
  kSin = 290,
  kAsStrided = 291,
  kDropoutGradExt = 292,
  kInplaceFillDiagonal = 293,
  kLogicalXor = 294,
  kSumExt = 295,
  kGridSampler2D = 296,
  kMultiScaleDeformableAttnGrad = 297,
  kMeanExt = 298,
  kGluGrad = 299,
  kReduceAny = 300,
  kLeakyReLUExt = 301,
  kLogSigmoid = 302,
  kVar = 303,
  kAvgPool2D = 304,
  kInplaceRandom = 305,
  kLogicalNot = 306,
  kAddScalar = 307,
  kMaxUnpool2DExt = 308,
  kBitwiseXorScalar = 309,
  kGreaterEqualScalar = 310,
  kSearchSorted = 311,
  kKLDivGrad = 312,
  kNormalFloatTensor = 313,
  kPowTensorScalar = 314,
  kRepeatInterleaveGrad = 315,
  kSoftMarginLossGrad = 316,
  kSelectExtView = 317,
  kMla = 318,
  kNotEqual = 319,
  kArange = 320,
  kLogAddExp2 = 321,
  kNLLLossGrad = 322,
  kSortExt = 323,
  kBitwiseAndTensor = 324,
  kProdExt = 325,
  kReluGrad = 326,
  kChunk = 327,
  kMaxPoolGradWithMask = 328,
  kConcat = 329,
  kAvgPool3DExt = 330,
  kReduceAll = 331,
  kTanhGrad = 332,
  kUniformExt = 333,
  kInplaceSign = 334,
  kBincountExt = 335,
  kOnes = 336,
  kMSELossExt = 337,
  kBatchMatMulExt = 338,
  kUpsampleBicubic2DGrad = 339,
  kMSELossGradExt = 340,
  kRandInt = 341,
  kInplaceFloor = 342,
  kFloor = 343,
  kInplaceFillTensor = 344,
  kInplaceClampScalar = 345,
  kFillScalar = 346,
  kHSigmoidGrad = 347,
  kFillTensor = 348,
  kMm = 349,
  kAdaptiveAvgPool2DExt = 350,
  kHSwishGrad = 351,
  kToDtype = 352,
  kInnerIndex = 353,
  kFlattenExt = 354,
  kConvolutionStrGrad = 354,
  kSelect = 355,
  kFullLike = 356,
  kStackExt = 357,
  kInplaceUniform = 358,
  kUpsampleNearest1DGrad = 359,
  kRsqrt = 360,
  kBitwiseXorTensor = 361,
  kScatterAddExt = 362,
  kSiLU = 363,
  kSplit = 364,
  kSqueeze = 365,
  kTrilExt = 366,
  kExpm1 = 367,
  kHSwish = 368,
  kClampScalar = 369,
  kHShrinkGrad = 370,
  kConvTranspose2D = 371,
  kUpsampleLinear1DGrad = 372,
  kFmodTensor = 373,
  kCrossEntropyLoss = 374,
  kNormalTensorFloat = 375,
  kMishGradExt = 376,
  kMaximum = 377,
  kRealView = 378,
  kBatchMatMul = 379,
  kRandnLike = 380,
  kAdaptiveAvgPool1D = 381,
  kTan = 382,
  kArgMaxWithValue = 383,
  kAddmm = 384,
  kMax = 385,
  kUpsampleNearest3DGrad = 386,
  kInplaceFloorDivide = 387,
  kGroupNormGrad = 388,
  kIsFinite = 389,
  kTensorScatterElements = 390,
  kMoeTokenUnpermuteGrad = 391,
  kSubScalar = 392,
  kElu = 393,
  kLog10 = 394,
  kInplaceBernoulliScalar = 395,
  kOneHotExt = 396,
  kRemainderTensorTensor = 397,
  kSub = 398,
  kGreater = 399,
  kInplaceScatterSrc = 400,
  kRandExt = 401,
  kLogicalAnd = 402,
  kMinDim = 403,
  kMoeTokenPermute = 404,
  kNanToNum = 405,
  kInplaceStopGradient = 406,
  kDivMod = 407,
  kAddLayerNormGrad = 408,
  kXLogYScalarSelf = 409,
  kCos = 410,
  kAllFinite = 411,
  kL1LossBackwardExt = 412,
  kLinalgQr = 413,
  kAtanExt = 414,
  kLogicalOr = 415,
  kAdd = 416,
  kUpsampleNearest1D = 417,
  kToDevice = 418,
  kInplaceIndexFillScalar = 419,
  kNLLLoss2dGrad = 420,
  kSliceExt = 421,
  kExpandDims = 422,
  kDense = 423,
  kReLU = 424,
  kLayerNormExt = 425,
  kAdaptiveAvgPool2DGradExt = 426,
  kHShrink = 427,
  kMishExt = 428,
  kCross = 429,
  kInplaceSubScalar = 430,
  kZerosLikeExt = 431,
  kExp2 = 432,
  kMatrixInverseExt = 433,
  kTranspose = 434,
  kReshapeAndCache = 435,
  kFlashAttentionScoreGrad = 436,
  kIsNegInf = 437,
  kOnesLikeExt = 438,
  kInnerNonZero = 439,
  kLogSigmoidGrad = 440,
  kRemainderTensorScalar = 441,
  kBCEWithLogitsLoss = 442,
  kInplaceElu = 443,
  kInplaceIndexPut = 444,
  kGcd = 445,
  kLess = 446,
  kSeLUExt = 447,
  kAddbmm = 448,
  kIndexFillScalar = 449,
  kInplaceSiLU = 450,
  kReflectionPad2D = 451,
  kDiagonalView = 452,
  kMaskedFill = 453,
  kEqualExt = 454,
  kLogSumExp = 455,
  kHSigmoid = 456,
  kBernoulliExt = 457,
  kTExt = 458,
  kUpsampleTrilinear3D = 458,
  kMoeDistributeDispatch = 459,
  kZeros = 460,
  kNonZero = 461,
  kSubExt = 462,
  kMultiScaleDeformableAttn = 463,
  kMul = 464,
  kReciprocal = 465,
  kTriangularSolve = 466,
  kRmsNormGrad = 467,
  kRepeatInterleaveInt = 468,
  kXLogYScalarOther = 469,
  kRepeat = 470,
  kExpandDimsView = 471,
  kBinaryCrossEntropyGrad = 472,
  kEye = 473,
  kViewAs = 474,
  kUpsampleNearest2DGrad = 474,
  kInplaceMaskedFillTensor = 475,
  kSilentCheckV2 = 476,
  kRandLikeExt = 477,
  kInplaceScatterValue = 478,
  kRepeatInterleaveTensor = 479,
  kPagedAttention = 480,
  kInplaceExp = 481,
  kRotaryPositionEmbeddingGrad = 482,
  kHistcExt = 483,
  kClone = 484,
  kInplaceDiv = 485,
  kGeLU = 486,
  kApplyRotaryPosEmb = 487,
  kEluGradExt = 488,
  kBatchNormGatherStatsWithCounts = 489,
  kRandpermExt = 490,
  kInplaceMuls = 491,
  kArgMinExt = 492,
  kAddcdivExt = 493,
  kConv1DPadding = 494,
  kSpeedFusionAttentionGrad = 495,
  kThreshold = 496,
  kConvolutionGrad = 497,
  kMaskedScatter = 498,
  kAddRmsNormQuantV2 = 499,
  kMatmulAllReduceAddRmsNorm = 500,
  kGroupedMatmul = 501,
  kQuantBatchMatmul = 502,
  kMoeInitRoutingV2 = 503,
  kFusedInferAttentionScore = 504,
  kMoeFinalizeRouting = 505,
  kMoeGatingTopKSoftmax = 506,
  kDynamicQuantExt = 507,
  kQuantMatmul = 508,
  kGroupedMatmulV4 = 509,
  kMoeInitRoutingQuantV2 = 510,
  kWeightQuantBatchMatmul = 511,
  kKVCacheScatterUpdate = 512,
  kMoeInitRouting = 513,
  kGroupedMatmulV2 = 514,
  kQuantV2 = 515,
  kMoeComputeExpertTokens = 516,
  kInnerCommAllReduce = 517,
  kDistCommAllGather = 518,
  kDistCommIrecv = 519,
  kDistCommBarrier = 520,
  kDistCommScatter = 521,
  kInnerCommAllGather = 522,
  kDistCommReduceScatterTensor = 523,
  kDistCommGather = 524,
  kDistCommReduce = 525,
  kDistCommReduceScatter = 526,
  kInnerCommIrecv = 527,
  kInnerCommReduceScatter = 528,
  kDistCommReduceScatterTensorUneven = 529,
  kDistCommAllReduce = 530,
  kDistCommBroadcast = 531,
  kDistCommAllToAllV = 532,
  kDistCommGatherIntoTensor = 533,
  kDistCommAllToAllVC = 534,
  kDistCommAllToAllVSingle = 535,
  kDistCommAllGatherIntoTensorUneven = 536,
  kDistCommBatchIsendIrecv = 537,
  kInnerCommIsend = 538,
  kDistCommIsend = 539,
  kInnerCommAllToAllV = 540,
  kDistCommAllGatherIntoTensor = 541,
  kDistCommScatterTensor = 542,
  kEinsumExt = 543,
  kGmmBackward = 544,
  kGmm = 545,
  kInplaceExponential = 546,
  kGmmV2Backward = 547,
  kGmmV2BackwardFusion = 548,
  kFuncDropoutExt = 549,
  kGmmV2 = 550,
  kMoeTokenUnpermute = 551,
  kAnyExt = 552,
  kDropout2dExt = 553,
  kAny = 554,
  kPixelShuffle = 555,
  kGmmBackwardFusion = 556,
  kFuncMaxPool2D = 557,
};

using DropoutGenMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceSubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using GroupNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using LessEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReflectionPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using CountNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using LinSpaceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using BatchNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &)>;
using Col2ImGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using InplaceMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using Log1pGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using SplitTensorGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using MatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GatherDGradV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MinimumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TraceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using SilentCheckV3GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using FracGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleLinear1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using CastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceRemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MaskedSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using InplaceIndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using MaxDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using Atan2ExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BitwiseNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using GeneratorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using GLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SliceGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const std::vector<int64_t> &)>;
using CrossEntropyLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using UpsampleTrilinear3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using AdaptiveMaxPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ArgMaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using DiagExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using NarrowGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using MaskedSelectGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using Unique2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MedianDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ImagViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using RandIntLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AddmvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BatchNormReduceGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using FloorDivScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using DivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using CoshGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using CellBackwardHookGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using SwigluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveAvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceScatterValueReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReverseV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using FlashAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Conv3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using CumminExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseOrTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReduceMinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using SigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TruncGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddcmulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ArgSortGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using LerpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleBilinear2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using InplaceRemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SplitTensorViewGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using InplaceAddsExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using RemainderScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using PolarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RandnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SliceExtViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &, const int64_t &)>;
using SplitWithSizeGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const int64_t &)>;
using IsInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using AvgPool2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SplitWithSizeViewGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const int64_t &)>;
using InplaceFloorDividesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using IsCloseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using NLLLoss2dGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using DivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReflectionPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaxPoolGradWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AcoshExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SmoothL1LossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GeluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BatchNormElemtGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EmbeddingDenseBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using ReflectionPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceAddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using IndexSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using ViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using InplaceMaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ChunkViewGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using NormalFloatFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MoeDistributeCombineGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::StringImmPtr> &, const std::optional<mindspore::StringImmPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeTokenPermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NonZeroExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleBicubic2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using DequantSwigluQuantGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using HardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BatchNormStatsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using CeilGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceIndexCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using TransposeExtViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using GridSampler3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using SpeedFusionAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AcosExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using Im2ColExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using GeluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using FloorDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplacePutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using TransposeViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using Conv3DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SoftShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using SwigluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using LogSoftmaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceDivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using LeakyReLUGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using RotaryPositionEmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using RoundGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ToOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceHardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ThresholdGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceBernoulliTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using FFNExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GreaterEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SincGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BroadcastToGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using Log2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TriuGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using CummaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InnerMoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BatchNormElemtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using UniqueConsecutiveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NegGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using TileGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using Conv2DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using GeLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using NewZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NewFullGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using Col2ImExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using UniqueDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AsinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftmaxBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using SiLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using PromptFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GatherDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using DropoutDoMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using ReplicationPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using SelectV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceLogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftplusExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using AdaptiveAvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceDivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using KLDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NewOnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GridSampler2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using ArgMinWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ReplicationPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using DotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AdamWGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MatmulReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NormalTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SmoothL1LossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using NormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LerpScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using UpsampleBilinear2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using SigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using PowScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using MulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using PReLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using OuterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GridSampler3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NeScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using MedianExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceMaskedScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using CopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using TakeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AllGatherMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MultinomialExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using CustomExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using SoftplusGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BinaryCrossEntropyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using NLLLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceDivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using HardtanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using RingAttentionUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using IdentityGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LinalgVectorNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using VarMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using BaddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using RollGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SinhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using IndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using TopkExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using EmptyLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using EmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using ConvolutionStrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using Conv1DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AbsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BinaryCrossEntropyWithLogitsBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using DivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using CumsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InnerUniqueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceTanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ContiguousGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using NansumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FmodScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using L1LossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using LogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AddLayerNormV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using MaxPoolWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterSrcReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceIndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UnstackExtViewGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using InplaceGroupedMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using StdMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using IndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ConvolutionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceMaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using LogSoftmaxGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using NarrowViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using LogSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseOrScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using KthvalueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using BitwiseAndScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ConstantPadNDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &)>;
using AtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftMarginLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InnerInplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using ErfcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AdaptiveMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReflectionPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using TypeAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using StdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using LogAddExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SquareGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BatchNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using EmptyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using ErfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceNormalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BroadcastToViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using LayerNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using DropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SeluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using IndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using NewEmptyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReshapeGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using MaxPoolWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using XlogyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AsinhExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using IncreFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Conv2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using MinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AsStridedGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const std::vector<int64_t> &, const int64_t &)>;
using DropoutGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceFillDiagonalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using LogicalXorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GridSampler2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using MultiScaleDeformableAttnGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MeanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ReduceAnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using LeakyReLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using LogSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using VarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AvgPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceRandomGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LogicalNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AddScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MaxUnpool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BitwiseXorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using GreaterEqualScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SearchSortedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using KLDivGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NormalFloatTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using PowTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using RepeatInterleaveGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using SoftMarginLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using SelectExtViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using MlaGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using NotEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ArangeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogAddExp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using NLLLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SortExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using BitwiseAndTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ProdExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ChunkGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using MaxPoolGradWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using ConcatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReduceAllGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using TanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UniformExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceSignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BincountExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using OnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MSELossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BatchMatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleBicubic2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using MSELossGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using RandIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceFloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using FloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using FillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using HSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using FillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AdaptiveAvgPool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using HSwishGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ToDtypeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InnerIndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ConvolutionStrGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using SelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using FullLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using StackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using InplaceUniformGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using RsqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BitwiseXorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ScatterAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SplitGradFunc = std::function<void(const std::vector<mindspore::tensor::TensorPtr> &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using SqueezeGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using TrilExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using Expm1GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using HSwishGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using HShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using ConvTranspose2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using UpsampleLinear1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using FmodTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using CrossEntropyLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using NormalTensorFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MishGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MaximumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RealViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BatchMatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using RandnLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AdaptiveAvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using TanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ArgMaxWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceFloorDivideGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GroupNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using IsFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TensorScatterElementsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeTokenUnpermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using EluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using Log10GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceBernoulliScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using OneHotExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using RemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SubGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GreaterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceScatterSrcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RandExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogicalAndGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MinDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using MoeTokenPermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using NanToNumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &)>;
using InplaceStopGradientGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using DivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AddLayerNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using XLogYScalarSelfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using CosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AllFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using L1LossBackwardExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using LinalgQrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using AtanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LogicalOrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ToDeviceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceIndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using NLLLoss2dGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using SliceExtGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &, const int64_t &)>;
using ExpandDimsGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using DenseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using ReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LayerNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using AdaptiveAvgPool2DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using HShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using MishExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using CrossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceSubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ZerosLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using Exp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MatrixInverseExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TransposeGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using ReshapeAndCacheGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using FlashAttentionScoreGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using IsNegInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using OnesLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InnerNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LogSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using BCEWithLogitsLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using InplaceEluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using GcdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LessGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SeLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using IndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceSiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReflectionPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using DiagonalViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using MaskedFillGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EqualExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LogSumExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using HSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BernoulliExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleTrilinear3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using MoeDistributeDispatchGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::StringImmPtr> &, const std::optional<mindspore::StringImmPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using MultiScaleDeformableAttnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReciprocalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TriangularSolveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using RmsNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RepeatInterleaveIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using XLogYScalarOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using RepeatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ExpandDimsViewGradFunc = std::function<void(const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using BinaryCrossEntropyGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using EyeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleNearest2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceMaskedFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SilentCheckV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RandLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using RepeatInterleaveTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using PagedAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using RotaryPositionEmbeddingGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using HistcExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using CloneGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GeLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ApplyRotaryPosEmbGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using EluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormGatherStatsWithCountsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using RandpermExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceMulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ArgMinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using AddcdivExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using Conv1DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SpeedFusionAttentionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ConvolutionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using MaskedScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddRmsNormQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using MatmulAllReduceAddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using QuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using FusedInferAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeFinalizeRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using MoeGatingTopKSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using DynamicQuantExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using QuantMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GroupedMatmulV4GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MoeInitRoutingQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using WeightQuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using KVCacheScatterUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using QuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeComputeExpertTokensGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InnerCommAllReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommAllGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommBarrierGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::StringImmPtr &)>;
using DistCommScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using InnerCommAllGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommReduceScatterTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using InnerCommIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using InnerCommReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommReduceScatterTensorUnevenGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommAllReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommBroadcastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommAllToAllVGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using DistCommGatherIntoTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommAllToAllVCGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommAllToAllVSingleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using DistCommAllGatherIntoTensorUnevenGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommBatchIsendIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using InnerCommIsendGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommIsendGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using InnerCommAllToAllVGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using DistCommAllGatherIntoTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommScatterTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using EinsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &)>;
using GmmBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &)>;
using GmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceExponentialGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GmmV2BackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using GmmV2BackwardFusionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using FuncDropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GmmV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AnyExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using Dropout2dExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PixelShuffleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using GmmBackwardFusionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &)>;
using FuncMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;

struct OpsAutoGradRegisters {
  DropoutGenMaskExtGradFunc DropoutGenMaskExtGradFuncObj;
  InplaceSubExtGradFunc InplaceSubExtGradFuncObj;
  GroupNormGradFunc GroupNormGradFuncObj;
  LessEqualGradFunc LessEqualGradFuncObj;
  ReflectionPad1DGradGradFunc ReflectionPad1DGradGradFuncObj;
  CountNonZeroGradFunc CountNonZeroGradFuncObj;
  LinSpaceExtGradFunc LinSpaceExtGradFuncObj;
  ReflectionPad1DGradFunc ReflectionPad1DGradFuncObj;
  BatchNormGradExtGradFunc BatchNormGradExtGradFuncObj;
  Col2ImGradGradFunc Col2ImGradGradFuncObj;
  InplaceMatmulAddGradFunc InplaceMatmulAddGradFuncObj;
  EqualGradFunc EqualGradFuncObj;
  InplaceSigmoidGradFunc InplaceSigmoidGradFuncObj;
  Log1pGradFunc Log1pGradFuncObj;
  SoftShrinkGradFunc SoftShrinkGradFuncObj;
  SplitTensorGradFunc SplitTensorGradFuncObj;
  MatMulExtGradFunc MatMulExtGradFuncObj;
  GatherDGradV2GradFunc GatherDGradV2GradFuncObj;
  ReplicationPad3DGradGradFunc ReplicationPad3DGradGradFuncObj;
  MinimumGradFunc MinimumGradFuncObj;
  InplaceErfinvGradFunc InplaceErfinvGradFuncObj;
  TraceExtGradFunc TraceExtGradFuncObj;
  UpsampleNearest3DGradFunc UpsampleNearest3DGradFuncObj;
  AddRmsNormGradFunc AddRmsNormGradFuncObj;
  SilentCheckV3GradFunc SilentCheckV3GradFuncObj;
  TanhGradFunc TanhGradFuncObj;
  FracGradFunc FracGradFuncObj;
  UpsampleLinear1DGradFunc UpsampleLinear1DGradFuncObj;
  CastGradFunc CastGradFuncObj;
  InplaceRemainderTensorScalarGradFunc InplaceRemainderTensorScalarGradFuncObj;
  SignGradFunc SignGradFuncObj;
  MaskedSelectGradFunc MaskedSelectGradFuncObj;
  InplaceClampTensorGradFunc InplaceClampTensorGradFuncObj;
  InplaceIndexAddExtGradFunc InplaceIndexAddExtGradFuncObj;
  MaxDimGradFunc MaxDimGradFuncObj;
  Atan2ExtGradFunc Atan2ExtGradFuncObj;
  BitwiseNotGradFunc BitwiseNotGradFuncObj;
  MatMulGradFunc MatMulGradFuncObj;
  GeneratorGradFunc GeneratorGradFuncObj;
  GLUGradFunc GLUGradFuncObj;
  InplaceThresholdGradFunc InplaceThresholdGradFuncObj;
  SliceGradFunc SliceGradFuncObj;
  CrossEntropyLossGradGradFunc CrossEntropyLossGradGradFuncObj;
  UpsampleTrilinear3DGradGradFunc UpsampleTrilinear3DGradGradFuncObj;
  AdaptiveMaxPool1DGradFunc AdaptiveMaxPool1DGradFuncObj;
  ArgMaxExtGradFunc ArgMaxExtGradFuncObj;
  DiagExtGradFunc DiagExtGradFuncObj;
  ScatterGradFunc ScatterGradFuncObj;
  NarrowGradFunc NarrowGradFuncObj;
  MaskedSelectGradGradFunc MaskedSelectGradGradFuncObj;
  InplaceFillScalarGradFunc InplaceFillScalarGradFuncObj;
  Unique2GradFunc Unique2GradFuncObj;
  MedianDimGradFunc MedianDimGradFuncObj;
  ImagViewGradFunc ImagViewGradFuncObj;
  RmsNormGradFunc RmsNormGradFuncObj;
  RandIntLikeGradFunc RandIntLikeGradFuncObj;
  AddmvGradFunc AddmvGradFuncObj;
  BatchNormReduceGradGradFunc BatchNormReduceGradGradFuncObj;
  FloorDivScalarGradFunc FloorDivScalarGradFuncObj;
  DivsGradFunc DivsGradFuncObj;
  CoshGradFunc CoshGradFuncObj;
  CellBackwardHookGradFunc CellBackwardHookGradFuncObj;
  SwigluGradFunc SwigluGradFuncObj;
  AdaptiveAvgPool3DGradExtGradFunc AdaptiveAvgPool3DGradExtGradFuncObj;
  EluExtGradFunc EluExtGradFuncObj;
  InplaceScatterValueReduceGradFunc InplaceScatterValueReduceGradFuncObj;
  InplaceReLUGradFunc InplaceReLUGradFuncObj;
  ReverseV2GradFunc ReverseV2GradFuncObj;
  FlashAttentionScoreGradFunc FlashAttentionScoreGradFuncObj;
  Conv3DExtGradFunc Conv3DExtGradFuncObj;
  CumminExtGradFunc CumminExtGradFuncObj;
  BitwiseOrTensorGradFunc BitwiseOrTensorGradFuncObj;
  ReduceMinGradFunc ReduceMinGradFuncObj;
  SigmoidGradFunc SigmoidGradFuncObj;
  TruncGradFunc TruncGradFuncObj;
  InplaceMulGradFunc InplaceMulGradFuncObj;
  AddcmulExtGradFunc AddcmulExtGradFuncObj;
  ArgSortGradFunc ArgSortGradFuncObj;
  LerpGradFunc LerpGradFuncObj;
  SqrtGradFunc SqrtGradFuncObj;
  UpsampleBilinear2DGradFunc UpsampleBilinear2DGradFuncObj;
  InplaceRemainderTensorTensorGradFunc InplaceRemainderTensorTensorGradFuncObj;
  SplitTensorViewGradFunc SplitTensorViewGradFuncObj;
  InplaceAddsExtGradFunc InplaceAddsExtGradFuncObj;
  RemainderScalarTensorGradFunc RemainderScalarTensorGradFuncObj;
  PolarGradFunc PolarGradFuncObj;
  RandnGradFunc RandnGradFuncObj;
  AvgPool3DGradExtGradFunc AvgPool3DGradExtGradFuncObj;
  SliceExtViewGradFunc SliceExtViewGradFuncObj;
  SplitWithSizeGradFunc SplitWithSizeGradFuncObj;
  IsInfGradFunc IsInfGradFuncObj;
  ReplicationPad1DGradGradFunc ReplicationPad1DGradGradFuncObj;
  AvgPool2DGradGradFunc AvgPool2DGradGradFuncObj;
  SplitWithSizeViewGradFunc SplitWithSizeViewGradFuncObj;
  InplaceFloorDividesGradFunc InplaceFloorDividesGradFuncObj;
  IsCloseGradFunc IsCloseGradFuncObj;
  NLLLoss2dGradFunc NLLLoss2dGradFuncObj;
  ClampTensorGradFunc ClampTensorGradFuncObj;
  DivGradFunc DivGradFuncObj;
  ReflectionPad2DGradGradFunc ReflectionPad2DGradGradFuncObj;
  MaxPoolGradWithIndicesGradFunc MaxPoolGradWithIndicesGradFuncObj;
  AcoshExtGradFunc AcoshExtGradFuncObj;
  SmoothL1LossGradGradFunc SmoothL1LossGradGradFuncObj;
  GeluGradExtGradFunc GeluGradExtGradFuncObj;
  BatchNormElemtGradGradFunc BatchNormElemtGradGradFuncObj;
  EmbeddingDenseBackwardGradFunc EmbeddingDenseBackwardGradFuncObj;
  ReflectionPad3DGradFunc ReflectionPad3DGradFuncObj;
  MvGradFunc MvGradFuncObj;
  ReplicationPad1DGradFunc ReplicationPad1DGradFuncObj;
  InplaceAddmmGradFunc InplaceAddmmGradFuncObj;
  IndexSelectGradFunc IndexSelectGradFuncObj;
  ViewGradFunc ViewGradFuncObj;
  InplaceMaskedFillScalarGradFunc InplaceMaskedFillScalarGradFuncObj;
  ChunkViewGradFunc ChunkViewGradFuncObj;
  NormalFloatFloatGradFunc NormalFloatFloatGradFuncObj;
  MoeDistributeCombineGradFunc MoeDistributeCombineGradFuncObj;
  MoeTokenPermuteGradGradFunc MoeTokenPermuteGradGradFuncObj;
  NonZeroExtGradFunc NonZeroExtGradFuncObj;
  UpsampleBicubic2DGradFunc UpsampleBicubic2DGradFuncObj;
  DequantSwigluQuantGradFunc DequantSwigluQuantGradFuncObj;
  AddExtGradFunc AddExtGradFuncObj;
  HardtanhGradFunc HardtanhGradFuncObj;
  BatchNormStatsGradFunc BatchNormStatsGradFuncObj;
  CeilGradFunc CeilGradFuncObj;
  InplaceIndexCopyGradFunc InplaceIndexCopyGradFuncObj;
  TransposeExtViewGradFunc TransposeExtViewGradFuncObj;
  GridSampler3DGradGradFunc GridSampler3DGradGradFuncObj;
  SpeedFusionAttentionGradFunc SpeedFusionAttentionGradFuncObj;
  AcosExtGradFunc AcosExtGradFuncObj;
  Im2ColExtGradFunc Im2ColExtGradFuncObj;
  GeluExtGradFunc GeluExtGradFuncObj;
  FloorDivGradFunc FloorDivGradFuncObj;
  InplacePutGradFunc InplacePutGradFuncObj;
  TransposeViewGradFunc TransposeViewGradFuncObj;
  Conv3DPaddingGradFunc Conv3DPaddingGradFuncObj;
  SoftShrinkGradGradFunc SoftShrinkGradGradFuncObj;
  SwigluGradGradFunc SwigluGradGradFuncObj;
  LogSoftmaxExtGradFunc LogSoftmaxExtGradFuncObj;
  InplaceDivsGradFunc InplaceDivsGradFuncObj;
  LeakyReLUGradExtGradFunc LeakyReLUGradExtGradFuncObj;
  RotaryPositionEmbeddingGradFunc RotaryPositionEmbeddingGradFuncObj;
  RoundGradFunc RoundGradFuncObj;
  ToOtherGradFunc ToOtherGradFuncObj;
  InplaceHardtanhGradFunc InplaceHardtanhGradFuncObj;
  ThresholdGradGradFunc ThresholdGradGradFuncObj;
  InplaceBernoulliTensorGradFunc InplaceBernoulliTensorGradFuncObj;
  InplaceZeroGradFunc InplaceZeroGradFuncObj;
  FFNExtGradFunc FFNExtGradFuncObj;
  GreaterEqualGradFunc GreaterEqualGradFuncObj;
  SincGradFunc SincGradFuncObj;
  BroadcastToGradFunc BroadcastToGradFuncObj;
  Log2GradFunc Log2GradFuncObj;
  TriuGradFunc TriuGradFuncObj;
  CummaxGradFunc CummaxGradFuncObj;
  InnerMoeTokenUnpermuteGradFunc InnerMoeTokenUnpermuteGradFuncObj;
  BatchNormElemtGradFunc BatchNormElemtGradFuncObj;
  UniqueConsecutiveGradFunc UniqueConsecutiveGradFuncObj;
  NegGradFunc NegGradFuncObj;
  ReplicationPad3DGradFunc ReplicationPad3DGradFuncObj;
  TileGradFunc TileGradFuncObj;
  Conv2DPaddingGradFunc Conv2DPaddingGradFuncObj;
  GeLUGradGradFunc GeLUGradGradFuncObj;
  NewZerosGradFunc NewZerosGradFuncObj;
  NewFullGradFunc NewFullGradFuncObj;
  Col2ImExtGradFunc Col2ImExtGradFuncObj;
  UniqueDimGradFunc UniqueDimGradFuncObj;
  AsinExtGradFunc AsinExtGradFuncObj;
  SoftmaxBackwardGradFunc SoftmaxBackwardGradFuncObj;
  SiLUGradGradFunc SiLUGradGradFuncObj;
  PromptFlashAttentionGradFunc PromptFlashAttentionGradFuncObj;
  GatherDGradFunc GatherDGradFuncObj;
  DropoutDoMaskExtGradFunc DropoutDoMaskExtGradFuncObj;
  ReplicationPad2DGradFunc ReplicationPad2DGradFuncObj;
  SelectV2GradFunc SelectV2GradFuncObj;
  InplaceLogGradFunc InplaceLogGradFuncObj;
  SoftplusExtGradFunc SoftplusExtGradFuncObj;
  MaskedFillScalarGradFunc MaskedFillScalarGradFuncObj;
  AdaptiveAvgPool3DExtGradFunc AdaptiveAvgPool3DExtGradFuncObj;
  InplaceDivModGradFunc InplaceDivModGradFuncObj;
  KLDivGradFunc KLDivGradFuncObj;
  NewOnesGradFunc NewOnesGradFuncObj;
  GridSampler2DGradGradFunc GridSampler2DGradGradFuncObj;
  ArgMinWithValueGradFunc ArgMinWithValueGradFuncObj;
  ReplicationPad2DGradGradFunc ReplicationPad2DGradGradFuncObj;
  DotGradFunc DotGradFuncObj;
  AdamWGradFunc AdamWGradFuncObj;
  MatmulReduceScatterGradFunc MatmulReduceScatterGradFuncObj;
  NormalTensorTensorGradFunc NormalTensorTensorGradFuncObj;
  SmoothL1LossGradFunc SmoothL1LossGradFuncObj;
  NormGradFunc NormGradFuncObj;
  LerpScalarGradFunc LerpScalarGradFuncObj;
  UpsampleBilinear2DGradGradFunc UpsampleBilinear2DGradGradFuncObj;
  SigmoidGradGradFunc SigmoidGradGradFuncObj;
  PowScalarTensorGradFunc PowScalarTensorGradFuncObj;
  MulsGradFunc MulsGradFuncObj;
  PReLUGradGradFunc PReLUGradGradFuncObj;
  InplaceAddExtGradFunc InplaceAddExtGradFuncObj;
  OuterGradFunc OuterGradFuncObj;
  GridSampler3DGradFunc GridSampler3DGradFuncObj;
  NeScalarGradFunc NeScalarGradFuncObj;
  MedianExtGradFunc MedianExtGradFuncObj;
  InplaceMaskedScatterGradFunc InplaceMaskedScatterGradFuncObj;
  CopyGradFunc CopyGradFuncObj;
  UpsampleNearest2DGradFunc UpsampleNearest2DGradFuncObj;
  TakeGradFunc TakeGradFuncObj;
  AllGatherMatmulGradFunc AllGatherMatmulGradFuncObj;
  MultinomialExtGradFunc MultinomialExtGradFuncObj;
  CustomExtGradFunc CustomExtGradFuncObj;
  SoftplusGradExtGradFunc SoftplusGradExtGradFuncObj;
  BinaryCrossEntropyGradFunc BinaryCrossEntropyGradFuncObj;
  NLLLossGradFunc NLLLossGradFuncObj;
  InplaceDivModsGradFunc InplaceDivModsGradFuncObj;
  HardtanhGradGradFunc HardtanhGradGradFuncObj;
  RingAttentionUpdateGradFunc RingAttentionUpdateGradFuncObj;
  IdentityGradFunc IdentityGradFuncObj;
  LinalgVectorNormGradFunc LinalgVectorNormGradFuncObj;
  VarMeanGradFunc VarMeanGradFuncObj;
  ScatterValueGradFunc ScatterValueGradFuncObj;
  BaddbmmGradFunc BaddbmmGradFuncObj;
  RollGradFunc RollGradFuncObj;
  SinhGradFunc SinhGradFuncObj;
  PowGradFunc PowGradFuncObj;
  IndexFillTensorGradFunc IndexFillTensorGradFuncObj;
  TopkExtGradFunc TopkExtGradFuncObj;
  EmptyLikeGradFunc EmptyLikeGradFuncObj;
  EmbeddingGradFunc EmbeddingGradFuncObj;
  ConvolutionStrGradFunc ConvolutionStrGradFuncObj;
  Conv1DExtGradFunc Conv1DExtGradFuncObj;
  AbsGradFunc AbsGradFuncObj;
  BinaryCrossEntropyWithLogitsBackwardGradFunc BinaryCrossEntropyWithLogitsBackwardGradFuncObj;
  DivModsGradFunc DivModsGradFuncObj;
  CumsumExtGradFunc CumsumExtGradFuncObj;
  InnerUniqueGradFunc InnerUniqueGradFuncObj;
  InplaceTanhGradFunc InplaceTanhGradFuncObj;
  ContiguousGradFunc ContiguousGradFuncObj;
  NansumGradFunc NansumGradFuncObj;
  FmodScalarGradFunc FmodScalarGradFuncObj;
  L1LossExtGradFunc L1LossExtGradFuncObj;
  LogGradFunc LogGradFuncObj;
  AddLayerNormV2GradFunc AddLayerNormV2GradFuncObj;
  MaxPoolWithIndicesGradFunc MaxPoolWithIndicesGradFuncObj;
  InplaceScatterSrcReduceGradFunc InplaceScatterSrcReduceGradFuncObj;
  InplaceIndexFillTensorGradFunc InplaceIndexFillTensorGradFuncObj;
  UnstackExtViewGradFunc UnstackExtViewGradFuncObj;
  InplaceGroupedMatmulAddGradFunc InplaceGroupedMatmulAddGradFuncObj;
  ErfinvGradFunc ErfinvGradFuncObj;
  StdMeanGradFunc StdMeanGradFuncObj;
  IndexGradFunc IndexGradFuncObj;
  ConvolutionGradFunc ConvolutionGradFuncObj;
  AvgPool1DGradFunc AvgPool1DGradFuncObj;
  ReduceMaxGradFunc ReduceMaxGradFuncObj;
  LogSoftmaxGradGradFunc LogSoftmaxGradGradFuncObj;
  InplaceCopyGradFunc InplaceCopyGradFuncObj;
  NarrowViewGradFunc NarrowViewGradFuncObj;
  LogSoftmaxGradFunc LogSoftmaxGradFuncObj;
  BitwiseOrScalarGradFunc BitwiseOrScalarGradFuncObj;
  SoftmaxGradFunc SoftmaxGradFuncObj;
  ExpGradFunc ExpGradFuncObj;
  KthvalueGradFunc KthvalueGradFuncObj;
  BitwiseAndScalarGradFunc BitwiseAndScalarGradFuncObj;
  ConstantPadNDGradFunc ConstantPadNDGradFuncObj;
  AtanhGradFunc AtanhGradFuncObj;
  SoftMarginLossGradFunc SoftMarginLossGradFuncObj;
  InnerInplaceIndexPutGradFunc InnerInplaceIndexPutGradFuncObj;
  ErfcGradFunc ErfcGradFuncObj;
  PReLUGradFunc PReLUGradFuncObj;
  AdaptiveMaxPool2DGradFunc AdaptiveMaxPool2DGradFuncObj;
  ReflectionPad3DGradGradFunc ReflectionPad3DGradGradFuncObj;
  TypeAsGradFunc TypeAsGradFuncObj;
  StdGradFunc StdGradFuncObj;
  LogAddExpGradFunc LogAddExpGradFuncObj;
  SquareGradFunc SquareGradFuncObj;
  BatchNormExtGradFunc BatchNormExtGradFuncObj;
  EmptyGradFunc EmptyGradFuncObj;
  ErfGradFunc ErfGradFuncObj;
  InplaceNormalGradFunc InplaceNormalGradFuncObj;
  BroadcastToViewGradFunc BroadcastToViewGradFuncObj;
  LayerNormGradExtGradFunc LayerNormGradExtGradFuncObj;
  DropoutExtGradFunc DropoutExtGradFuncObj;
  SeluGradGradFunc SeluGradGradFuncObj;
  IndexAddExtGradFunc IndexAddExtGradFuncObj;
  NewEmptyGradFunc NewEmptyGradFuncObj;
  ReshapeGradFunc ReshapeGradFuncObj;
  MaxPoolWithMaskGradFunc MaxPoolWithMaskGradFuncObj;
  InplaceScatterAddGradFunc InplaceScatterAddGradFuncObj;
  XlogyGradFunc XlogyGradFuncObj;
  AsinhExtGradFunc AsinhExtGradFuncObj;
  IncreFlashAttentionGradFunc IncreFlashAttentionGradFuncObj;
  Conv2DExtGradFunc Conv2DExtGradFuncObj;
  MinGradFunc MinGradFuncObj;
  SinGradFunc SinGradFuncObj;
  AsStridedGradFunc AsStridedGradFuncObj;
  DropoutGradExtGradFunc DropoutGradExtGradFuncObj;
  InplaceFillDiagonalGradFunc InplaceFillDiagonalGradFuncObj;
  LogicalXorGradFunc LogicalXorGradFuncObj;
  SumExtGradFunc SumExtGradFuncObj;
  GridSampler2DGradFunc GridSampler2DGradFuncObj;
  MultiScaleDeformableAttnGradGradFunc MultiScaleDeformableAttnGradGradFuncObj;
  MeanExtGradFunc MeanExtGradFuncObj;
  GluGradGradFunc GluGradGradFuncObj;
  ReduceAnyGradFunc ReduceAnyGradFuncObj;
  LeakyReLUExtGradFunc LeakyReLUExtGradFuncObj;
  LogSigmoidGradFunc LogSigmoidGradFuncObj;
  VarGradFunc VarGradFuncObj;
  AvgPool2DGradFunc AvgPool2DGradFuncObj;
  InplaceRandomGradFunc InplaceRandomGradFuncObj;
  LogicalNotGradFunc LogicalNotGradFuncObj;
  AddScalarGradFunc AddScalarGradFuncObj;
  MaxUnpool2DExtGradFunc MaxUnpool2DExtGradFuncObj;
  BitwiseXorScalarGradFunc BitwiseXorScalarGradFuncObj;
  GreaterEqualScalarGradFunc GreaterEqualScalarGradFuncObj;
  SearchSortedGradFunc SearchSortedGradFuncObj;
  KLDivGradGradFunc KLDivGradGradFuncObj;
  NormalFloatTensorGradFunc NormalFloatTensorGradFuncObj;
  PowTensorScalarGradFunc PowTensorScalarGradFuncObj;
  RepeatInterleaveGradGradFunc RepeatInterleaveGradGradFuncObj;
  SoftMarginLossGradGradFunc SoftMarginLossGradGradFuncObj;
  SelectExtViewGradFunc SelectExtViewGradFuncObj;
  MlaGradFunc MlaGradFuncObj;
  NotEqualGradFunc NotEqualGradFuncObj;
  ArangeGradFunc ArangeGradFuncObj;
  LogAddExp2GradFunc LogAddExp2GradFuncObj;
  NLLLossGradGradFunc NLLLossGradGradFuncObj;
  SortExtGradFunc SortExtGradFuncObj;
  BitwiseAndTensorGradFunc BitwiseAndTensorGradFuncObj;
  ProdExtGradFunc ProdExtGradFuncObj;
  ReluGradGradFunc ReluGradGradFuncObj;
  ChunkGradFunc ChunkGradFuncObj;
  MaxPoolGradWithMaskGradFunc MaxPoolGradWithMaskGradFuncObj;
  ConcatGradFunc ConcatGradFuncObj;
  AvgPool3DExtGradFunc AvgPool3DExtGradFuncObj;
  ReduceAllGradFunc ReduceAllGradFuncObj;
  TanhGradGradFunc TanhGradGradFuncObj;
  UniformExtGradFunc UniformExtGradFuncObj;
  InplaceSignGradFunc InplaceSignGradFuncObj;
  BincountExtGradFunc BincountExtGradFuncObj;
  OnesGradFunc OnesGradFuncObj;
  MSELossExtGradFunc MSELossExtGradFuncObj;
  BatchMatMulExtGradFunc BatchMatMulExtGradFuncObj;
  UpsampleBicubic2DGradGradFunc UpsampleBicubic2DGradGradFuncObj;
  MSELossGradExtGradFunc MSELossGradExtGradFuncObj;
  RandIntGradFunc RandIntGradFuncObj;
  InplaceFloorGradFunc InplaceFloorGradFuncObj;
  FloorGradFunc FloorGradFuncObj;
  InplaceFillTensorGradFunc InplaceFillTensorGradFuncObj;
  InplaceClampScalarGradFunc InplaceClampScalarGradFuncObj;
  FillScalarGradFunc FillScalarGradFuncObj;
  HSigmoidGradGradFunc HSigmoidGradGradFuncObj;
  FillTensorGradFunc FillTensorGradFuncObj;
  MmGradFunc MmGradFuncObj;
  AdaptiveAvgPool2DExtGradFunc AdaptiveAvgPool2DExtGradFuncObj;
  HSwishGradGradFunc HSwishGradGradFuncObj;
  ToDtypeGradFunc ToDtypeGradFuncObj;
  InnerIndexGradFunc InnerIndexGradFuncObj;
  ConvolutionStrGradGradFunc ConvolutionStrGradGradFuncObj;
  SelectGradFunc SelectGradFuncObj;
  FullLikeGradFunc FullLikeGradFuncObj;
  StackExtGradFunc StackExtGradFuncObj;
  InplaceUniformGradFunc InplaceUniformGradFuncObj;
  UpsampleNearest1DGradGradFunc UpsampleNearest1DGradGradFuncObj;
  RsqrtGradFunc RsqrtGradFuncObj;
  BitwiseXorTensorGradFunc BitwiseXorTensorGradFuncObj;
  ScatterAddExtGradFunc ScatterAddExtGradFuncObj;
  SiLUGradFunc SiLUGradFuncObj;
  SplitGradFunc SplitGradFuncObj;
  SqueezeGradFunc SqueezeGradFuncObj;
  TrilExtGradFunc TrilExtGradFuncObj;
  Expm1GradFunc Expm1GradFuncObj;
  HSwishGradFunc HSwishGradFuncObj;
  ClampScalarGradFunc ClampScalarGradFuncObj;
  HShrinkGradGradFunc HShrinkGradGradFuncObj;
  ConvTranspose2DGradFunc ConvTranspose2DGradFuncObj;
  UpsampleLinear1DGradGradFunc UpsampleLinear1DGradGradFuncObj;
  FmodTensorGradFunc FmodTensorGradFuncObj;
  CrossEntropyLossGradFunc CrossEntropyLossGradFuncObj;
  NormalTensorFloatGradFunc NormalTensorFloatGradFuncObj;
  MishGradExtGradFunc MishGradExtGradFuncObj;
  MaximumGradFunc MaximumGradFuncObj;
  RealViewGradFunc RealViewGradFuncObj;
  BatchMatMulGradFunc BatchMatMulGradFuncObj;
  RandnLikeGradFunc RandnLikeGradFuncObj;
  AdaptiveAvgPool1DGradFunc AdaptiveAvgPool1DGradFuncObj;
  TanGradFunc TanGradFuncObj;
  ArgMaxWithValueGradFunc ArgMaxWithValueGradFuncObj;
  AddmmGradFunc AddmmGradFuncObj;
  MaxGradFunc MaxGradFuncObj;
  UpsampleNearest3DGradGradFunc UpsampleNearest3DGradGradFuncObj;
  InplaceFloorDivideGradFunc InplaceFloorDivideGradFuncObj;
  GroupNormGradGradFunc GroupNormGradGradFuncObj;
  IsFiniteGradFunc IsFiniteGradFuncObj;
  TensorScatterElementsGradFunc TensorScatterElementsGradFuncObj;
  MoeTokenUnpermuteGradGradFunc MoeTokenUnpermuteGradGradFuncObj;
  SubScalarGradFunc SubScalarGradFuncObj;
  EluGradFunc EluGradFuncObj;
  Log10GradFunc Log10GradFuncObj;
  InplaceBernoulliScalarGradFunc InplaceBernoulliScalarGradFuncObj;
  OneHotExtGradFunc OneHotExtGradFuncObj;
  RemainderTensorTensorGradFunc RemainderTensorTensorGradFuncObj;
  SubGradFunc SubGradFuncObj;
  GreaterGradFunc GreaterGradFuncObj;
  InplaceScatterSrcGradFunc InplaceScatterSrcGradFuncObj;
  RandExtGradFunc RandExtGradFuncObj;
  LogicalAndGradFunc LogicalAndGradFuncObj;
  MinDimGradFunc MinDimGradFuncObj;
  MoeTokenPermuteGradFunc MoeTokenPermuteGradFuncObj;
  NanToNumGradFunc NanToNumGradFuncObj;
  InplaceStopGradientGradFunc InplaceStopGradientGradFuncObj;
  DivModGradFunc DivModGradFuncObj;
  AddLayerNormGradGradFunc AddLayerNormGradGradFuncObj;
  XLogYScalarSelfGradFunc XLogYScalarSelfGradFuncObj;
  CosGradFunc CosGradFuncObj;
  AllFiniteGradFunc AllFiniteGradFuncObj;
  L1LossBackwardExtGradFunc L1LossBackwardExtGradFuncObj;
  LinalgQrGradFunc LinalgQrGradFuncObj;
  AtanExtGradFunc AtanExtGradFuncObj;
  LogicalOrGradFunc LogicalOrGradFuncObj;
  AddGradFunc AddGradFuncObj;
  UpsampleNearest1DGradFunc UpsampleNearest1DGradFuncObj;
  ToDeviceGradFunc ToDeviceGradFuncObj;
  InplaceIndexFillScalarGradFunc InplaceIndexFillScalarGradFuncObj;
  NLLLoss2dGradGradFunc NLLLoss2dGradGradFuncObj;
  SliceExtGradFunc SliceExtGradFuncObj;
  ExpandDimsGradFunc ExpandDimsGradFuncObj;
  DenseGradFunc DenseGradFuncObj;
  ReLUGradFunc ReLUGradFuncObj;
  LayerNormExtGradFunc LayerNormExtGradFuncObj;
  AdaptiveAvgPool2DGradExtGradFunc AdaptiveAvgPool2DGradExtGradFuncObj;
  HShrinkGradFunc HShrinkGradFuncObj;
  MishExtGradFunc MishExtGradFuncObj;
  CrossGradFunc CrossGradFuncObj;
  InplaceSubScalarGradFunc InplaceSubScalarGradFuncObj;
  ZerosLikeExtGradFunc ZerosLikeExtGradFuncObj;
  Exp2GradFunc Exp2GradFuncObj;
  MatrixInverseExtGradFunc MatrixInverseExtGradFuncObj;
  TransposeGradFunc TransposeGradFuncObj;
  ReshapeAndCacheGradFunc ReshapeAndCacheGradFuncObj;
  FlashAttentionScoreGradGradFunc FlashAttentionScoreGradGradFuncObj;
  IsNegInfGradFunc IsNegInfGradFuncObj;
  OnesLikeExtGradFunc OnesLikeExtGradFuncObj;
  InnerNonZeroGradFunc InnerNonZeroGradFuncObj;
  LogSigmoidGradGradFunc LogSigmoidGradGradFuncObj;
  RemainderTensorScalarGradFunc RemainderTensorScalarGradFuncObj;
  BCEWithLogitsLossGradFunc BCEWithLogitsLossGradFuncObj;
  InplaceEluGradFunc InplaceEluGradFuncObj;
  InplaceIndexPutGradFunc InplaceIndexPutGradFuncObj;
  GcdGradFunc GcdGradFuncObj;
  LessGradFunc LessGradFuncObj;
  SeLUExtGradFunc SeLUExtGradFuncObj;
  AddbmmGradFunc AddbmmGradFuncObj;
  IndexFillScalarGradFunc IndexFillScalarGradFuncObj;
  InplaceSiLUGradFunc InplaceSiLUGradFuncObj;
  ReflectionPad2DGradFunc ReflectionPad2DGradFuncObj;
  DiagonalViewGradFunc DiagonalViewGradFuncObj;
  MaskedFillGradFunc MaskedFillGradFuncObj;
  EqualExtGradFunc EqualExtGradFuncObj;
  LogSumExpGradFunc LogSumExpGradFuncObj;
  HSigmoidGradFunc HSigmoidGradFuncObj;
  BernoulliExtGradFunc BernoulliExtGradFuncObj;
  UpsampleTrilinear3DGradFunc UpsampleTrilinear3DGradFuncObj;
  MoeDistributeDispatchGradFunc MoeDistributeDispatchGradFuncObj;
  ZerosGradFunc ZerosGradFuncObj;
  NonZeroGradFunc NonZeroGradFuncObj;
  SubExtGradFunc SubExtGradFuncObj;
  MultiScaleDeformableAttnGradFunc MultiScaleDeformableAttnGradFuncObj;
  MulGradFunc MulGradFuncObj;
  ReciprocalGradFunc ReciprocalGradFuncObj;
  TriangularSolveGradFunc TriangularSolveGradFuncObj;
  RmsNormGradGradFunc RmsNormGradGradFuncObj;
  RepeatInterleaveIntGradFunc RepeatInterleaveIntGradFuncObj;
  XLogYScalarOtherGradFunc XLogYScalarOtherGradFuncObj;
  RepeatGradFunc RepeatGradFuncObj;
  ExpandDimsViewGradFunc ExpandDimsViewGradFuncObj;
  BinaryCrossEntropyGradGradFunc BinaryCrossEntropyGradGradFuncObj;
  EyeGradFunc EyeGradFuncObj;
  UpsampleNearest2DGradGradFunc UpsampleNearest2DGradGradFuncObj;
  InplaceMaskedFillTensorGradFunc InplaceMaskedFillTensorGradFuncObj;
  SilentCheckV2GradFunc SilentCheckV2GradFuncObj;
  RandLikeExtGradFunc RandLikeExtGradFuncObj;
  InplaceScatterValueGradFunc InplaceScatterValueGradFuncObj;
  RepeatInterleaveTensorGradFunc RepeatInterleaveTensorGradFuncObj;
  PagedAttentionGradFunc PagedAttentionGradFuncObj;
  InplaceExpGradFunc InplaceExpGradFuncObj;
  RotaryPositionEmbeddingGradGradFunc RotaryPositionEmbeddingGradGradFuncObj;
  HistcExtGradFunc HistcExtGradFuncObj;
  CloneGradFunc CloneGradFuncObj;
  InplaceDivGradFunc InplaceDivGradFuncObj;
  GeLUGradFunc GeLUGradFuncObj;
  ApplyRotaryPosEmbGradFunc ApplyRotaryPosEmbGradFuncObj;
  EluGradExtGradFunc EluGradExtGradFuncObj;
  BatchNormGatherStatsWithCountsGradFunc BatchNormGatherStatsWithCountsGradFuncObj;
  RandpermExtGradFunc RandpermExtGradFuncObj;
  InplaceMulsGradFunc InplaceMulsGradFuncObj;
  ArgMinExtGradFunc ArgMinExtGradFuncObj;
  AddcdivExtGradFunc AddcdivExtGradFuncObj;
  Conv1DPaddingGradFunc Conv1DPaddingGradFuncObj;
  SpeedFusionAttentionGradGradFunc SpeedFusionAttentionGradGradFuncObj;
  ThresholdGradFunc ThresholdGradFuncObj;
  ConvolutionGradGradFunc ConvolutionGradGradFuncObj;
  MaskedScatterGradFunc MaskedScatterGradFuncObj;
  AddRmsNormQuantV2GradFunc AddRmsNormQuantV2GradFuncObj;
  MatmulAllReduceAddRmsNormGradFunc MatmulAllReduceAddRmsNormGradFuncObj;
  GroupedMatmulGradFunc GroupedMatmulGradFuncObj;
  QuantBatchMatmulGradFunc QuantBatchMatmulGradFuncObj;
  MoeInitRoutingV2GradFunc MoeInitRoutingV2GradFuncObj;
  FusedInferAttentionScoreGradFunc FusedInferAttentionScoreGradFuncObj;
  MoeFinalizeRoutingGradFunc MoeFinalizeRoutingGradFuncObj;
  MoeGatingTopKSoftmaxGradFunc MoeGatingTopKSoftmaxGradFuncObj;
  DynamicQuantExtGradFunc DynamicQuantExtGradFuncObj;
  QuantMatmulGradFunc QuantMatmulGradFuncObj;
  GroupedMatmulV4GradFunc GroupedMatmulV4GradFuncObj;
  MoeInitRoutingQuantV2GradFunc MoeInitRoutingQuantV2GradFuncObj;
  WeightQuantBatchMatmulGradFunc WeightQuantBatchMatmulGradFuncObj;
  KVCacheScatterUpdateGradFunc KVCacheScatterUpdateGradFuncObj;
  MoeInitRoutingGradFunc MoeInitRoutingGradFuncObj;
  GroupedMatmulV2GradFunc GroupedMatmulV2GradFuncObj;
  QuantV2GradFunc QuantV2GradFuncObj;
  MoeComputeExpertTokensGradFunc MoeComputeExpertTokensGradFuncObj;
  InnerCommAllReduceGradFunc InnerCommAllReduceGradFuncObj;
  DistCommAllGatherGradFunc DistCommAllGatherGradFuncObj;
  DistCommIrecvGradFunc DistCommIrecvGradFuncObj;
  DistCommBarrierGradFunc DistCommBarrierGradFuncObj;
  DistCommScatterGradFunc DistCommScatterGradFuncObj;
  InnerCommAllGatherGradFunc InnerCommAllGatherGradFuncObj;
  DistCommReduceScatterTensorGradFunc DistCommReduceScatterTensorGradFuncObj;
  DistCommGatherGradFunc DistCommGatherGradFuncObj;
  DistCommReduceGradFunc DistCommReduceGradFuncObj;
  DistCommReduceScatterGradFunc DistCommReduceScatterGradFuncObj;
  InnerCommIrecvGradFunc InnerCommIrecvGradFuncObj;
  InnerCommReduceScatterGradFunc InnerCommReduceScatterGradFuncObj;
  DistCommReduceScatterTensorUnevenGradFunc DistCommReduceScatterTensorUnevenGradFuncObj;
  DistCommAllReduceGradFunc DistCommAllReduceGradFuncObj;
  DistCommBroadcastGradFunc DistCommBroadcastGradFuncObj;
  DistCommAllToAllVGradFunc DistCommAllToAllVGradFuncObj;
  DistCommGatherIntoTensorGradFunc DistCommGatherIntoTensorGradFuncObj;
  DistCommAllToAllVCGradFunc DistCommAllToAllVCGradFuncObj;
  DistCommAllToAllVSingleGradFunc DistCommAllToAllVSingleGradFuncObj;
  DistCommAllGatherIntoTensorUnevenGradFunc DistCommAllGatherIntoTensorUnevenGradFuncObj;
  DistCommBatchIsendIrecvGradFunc DistCommBatchIsendIrecvGradFuncObj;
  InnerCommIsendGradFunc InnerCommIsendGradFuncObj;
  DistCommIsendGradFunc DistCommIsendGradFuncObj;
  InnerCommAllToAllVGradFunc InnerCommAllToAllVGradFuncObj;
  DistCommAllGatherIntoTensorGradFunc DistCommAllGatherIntoTensorGradFuncObj;
  DistCommScatterTensorGradFunc DistCommScatterTensorGradFuncObj;
  EinsumExtGradFunc EinsumExtGradFuncObj;
  GmmBackwardGradFunc GmmBackwardGradFuncObj;
  GmmGradFunc GmmGradFuncObj;
  InplaceExponentialGradFunc InplaceExponentialGradFuncObj;
  GmmV2BackwardGradFunc GmmV2BackwardGradFuncObj;
  GmmV2BackwardFusionGradFunc GmmV2BackwardFusionGradFuncObj;
  FuncDropoutExtGradFunc FuncDropoutExtGradFuncObj;
  GmmV2GradFunc GmmV2GradFuncObj;
  MoeTokenUnpermuteGradFunc MoeTokenUnpermuteGradFuncObj;
  AnyExtGradFunc AnyExtGradFuncObj;
  Dropout2dExtGradFunc Dropout2dExtGradFuncObj;
  AnyGradFunc AnyGradFuncObj;
  PixelShuffleGradFunc PixelShuffleGradFuncObj;
  GmmBackwardFusionGradFunc GmmBackwardFusionGradFuncObj;
  FuncMaxPool2DGradFunc FuncMaxPool2DGradFuncObj;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
