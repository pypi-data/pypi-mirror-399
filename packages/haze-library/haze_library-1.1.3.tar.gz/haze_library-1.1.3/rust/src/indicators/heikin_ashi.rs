// indicators/heikin_ashi.rs - Heikin Ashi Candlesticks
//
// Heikin Ashi（平均K线）是一种平滑蜡烛图技术
// - 用于过滤市场噪音
// - 更清晰地显示趋势
// - 减少假信号

use crate::errors::validation::{validate_lengths_match, validate_not_empty};
use crate::errors::{HazeError, HazeResult};

/// Heikin Ashi 蜡烛图数据
#[derive(Debug, Clone)]
pub struct HeikinAshiCandles {
    pub ha_open: Vec<f64>,
    pub ha_high: Vec<f64>,
    pub ha_low: Vec<f64>,
    pub ha_close: Vec<f64>,
}

/// Heikin Ashi 信号结果
#[derive(Debug, Clone)]
pub struct HeikinAshiSignals {
    pub candles: HeikinAshiCandles,
    pub buy_signals: Vec<f64>,    // 买入信号（1.0 = 强烈买入）
    pub sell_signals: Vec<f64>,   // 卖出信号（1.0 = 强烈卖出）
    pub trend_strength: Vec<f64>, // 趋势强度（0.0-1.0）
}

/// 计算 Heikin Ashi 蜡烛图
///
/// # 参数
/// - `open`: 开盘价
/// - `high`: 最高价
/// - `low`: 最低价
/// - `close`: 收盘价
///
/// # 返回
/// HeikinAshiCandles 包含平滑后的 OHLC 数据
///
/// # 算法
/// ```text
/// HA_Close = (O + H + L + C) / 4
/// HA_Open = (HA_Open[prev] + HA_Close[prev]) / 2
/// HA_High = max(H, HA_Open, HA_Close)
/// HA_Low = min(L, HA_Open, HA_Close)
/// ```
pub fn heikin_ashi(
    open: &[f64],
    high: &[f64],
    low: &[f64],
    close: &[f64],
) -> HazeResult<HeikinAshiCandles> {
    validate_not_empty(close, "close")?;
    validate_lengths_match(&[
        (open, "open"),
        (high, "high"),
        (low, "low"),
        (close, "close"),
    ])?;

    let len = close.len();
    let mut ha_open = vec![0.0; len];
    let mut ha_high = vec![0.0; len];
    let mut ha_low = vec![0.0; len];
    let mut ha_close = vec![0.0; len];

    // 第一根蜡烛
    ha_open[0] = (open[0] + close[0]) / 2.0;
    ha_close[0] = (open[0] + high[0] + low[0] + close[0]) / 4.0;
    ha_high[0] = high[0];
    ha_low[0] = low[0];

    // 后续蜡烛
    for i in 1..len {
        // HA Close
        ha_close[i] = (open[i] + high[i] + low[i] + close[i]) / 4.0;

        // HA Open
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0;

        // HA High
        ha_high[i] = high[i].max(ha_open[i]).max(ha_close[i]);

        // HA Low
        ha_low[i] = low[i].min(ha_open[i]).min(ha_close[i]);
    }

    Ok(HeikinAshiCandles {
        ha_open,
        ha_high,
        ha_low,
        ha_close,
    })
}

/// Heikin Ashi 趋势信号
///
/// # 参数
/// - `open`, `high`, `low`, `close`: 原始OHLC数据
/// - `lookback`: 回看周期，用于判断连续趋势（默认 3）
///
/// # 返回
/// HeikinAshiSignals 包含买卖信号和趋势强度
///
/// # 信号规则
/// - 买入：连续N根看涨HA蜡烛（HA_Close > HA_Open，无下影线）
/// - 卖出：连续N根看跌HA蜡烛（HA_Close < HA_Open，无上影线）
/// - 趋势强度：蜡烛实体大小 / 蜡烛总高度
pub fn heikin_ashi_signals(
    open: &[f64],
    high: &[f64],
    low: &[f64],
    close: &[f64],
    lookback: usize,
) -> HazeResult<HeikinAshiSignals> {
    let candles = heikin_ashi(open, high, low, close)?;
    let len = close.len();

    let mut buy_signals = vec![0.0; len];
    let mut sell_signals = vec![0.0; len];
    let mut trend_strength = vec![0.0; len];

    for i in lookback..len {
        // 计算当前蜡烛的趋势强度
        let ha_body = (candles.ha_close[i] - candles.ha_open[i]).abs();
        let ha_range = candles.ha_high[i] - candles.ha_low[i];

        if ha_range > 0.0 {
            trend_strength[i] = ha_body / ha_range;
        }

        // 检查连续趋势
        let mut bullish_count = 0;
        let mut bearish_count = 0;

        for j in 0..lookback {
            let idx = i - j;
            let is_bullish = candles.ha_close[idx] > candles.ha_open[idx];
            let is_bearish = candles.ha_close[idx] < candles.ha_open[idx];

            // 检查是否有下影线（看涨蜡烛）或上影线（看跌蜡烛）
            let lower_shadow =
                candles.ha_open[idx].min(candles.ha_close[idx]) - candles.ha_low[idx];
            let upper_shadow =
                candles.ha_high[idx] - candles.ha_open[idx].max(candles.ha_close[idx]);

            if is_bullish && lower_shadow < ha_range * 0.1 {
                bullish_count += 1;
            }

            if is_bearish && upper_shadow < ha_range * 0.1 {
                bearish_count += 1;
            }
        }

        // 生成信号
        if bullish_count >= lookback {
            // 连续看涨蜡烛
            buy_signals[i] = 1.0;
        } else if bullish_count >= lookback / 2 {
            // 部分看涨
            buy_signals[i] = 0.5;
        }

        if bearish_count >= lookback {
            // 连续看跌蜡烛
            sell_signals[i] = 1.0;
        } else if bearish_count >= lookback / 2 {
            // 部分看跌
            sell_signals[i] = 0.5;
        }
    }

    Ok(HeikinAshiSignals {
        candles,
        buy_signals,
        sell_signals,
        trend_strength,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_heikin_ashi_basic() {
        let open = vec![100.0, 101.0, 102.0, 103.0, 104.0];
        let high = vec![102.0, 103.0, 104.0, 105.0, 106.0];
        let low = vec![99.0, 100.0, 101.0, 102.0, 103.0];
        let close = vec![101.0, 102.0, 103.0, 104.0, 105.0];

        let result = heikin_ashi(&open, &high, &low, &close).unwrap();

        // HA蜡烛应该平滑原始数据
        assert_eq!(result.ha_open.len(), 5);
        assert_eq!(result.ha_close.len(), 5);

        // 第一根蜡烛
        assert!((result.ha_open[0] - 100.5).abs() < 0.01);

        // 后续蜡烛应该使用前一根的HA值
        assert!(result.ha_open[1].is_finite());
    }

    #[test]
    fn test_heikin_ashi_signals_uptrend() {
        // 模拟上升趋势
        let len = 20;
        let open: Vec<f64> = (0..len).map(|i| 100.0 + i as f64).collect();
        let high: Vec<f64> = (0..len).map(|i| 100.0 + i as f64 + 2.0).collect();
        let low: Vec<f64> = (0..len).map(|i| 100.0 + i as f64 - 1.0).collect();
        let close: Vec<f64> = (0..len).map(|i| 100.0 + i as f64 + 1.0).collect();

        let result = heikin_ashi_signals(&open, &high, &low, &close, 3).unwrap();

        // 上升趋势应该有买入信号
        let buy_count: usize = result.buy_signals.iter().filter(|&&x| x > 0.0).count();

        assert!(buy_count > 0, "Expected buy signals in uptrend");
    }

    #[test]
    fn test_heikin_ashi_signals_downtrend() {
        // 模拟下降趋势
        let len = 20;
        let open: Vec<f64> = (0..len).map(|i| 120.0 - i as f64).collect();
        let high: Vec<f64> = (0..len).map(|i| 120.0 - i as f64 + 1.0).collect();
        let low: Vec<f64> = (0..len).map(|i| 120.0 - i as f64 - 2.0).collect();
        let close: Vec<f64> = (0..len).map(|i| 120.0 - i as f64 - 1.0).collect();

        let result = heikin_ashi_signals(&open, &high, &low, &close, 3).unwrap();

        // 下降趋势应该有卖出信号
        let sell_count: usize = result.sell_signals.iter().filter(|&&x| x > 0.0).count();

        assert!(sell_count > 0, "Expected sell signals in downtrend");
    }
}
