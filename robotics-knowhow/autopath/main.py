import argparse
import json
from .search import SearchPolicy
from .scenarios import get_default_scenarios
from .evaluator import Evaluator

def main():
    parser = argparse.ArgumentParser(description='AutoPath: Self-evolving DWA path planner')
    parser.add_argument('--mode', choices=['search', 'evaluate', 'demo'], default='search',
                        help='运行模式: search(搜索最优参数), evaluate(评估参数), demo(演示)')
    parser.add_argument('--method', choices=['genetic', 'hillclimb'], default='genetic',
                        help='搜索方法')
    parser.add_argument('--generations', type=int, default=20, help='遗传代数')
    parser.add_argument('--iterations', type=int, default=50, help='爬山迭代次数')
    parser.add_argument('--params', type=str, default=None, help='参数文件路径')
    args = parser.parse_args()
    
    scenarios = get_default_scenarios()
    
    if args.mode == 'search':
        print("启动自进化参数搜索...")
        searcher = SearchPolicy(scenarios)
        
        if args.method == 'genetic':
            best_params, best_score = searcher.genetic_search(generations=args.generations)
        else:
            best_params, best_score = searcher.hill_climb(iterations=args.iterations)
        
        searcher.save_results('results.tsv')
        searcher.save_best_params('best_params.json')
        
        print("\n搜索完成!")
        print(f"最佳得分: {best_score:.2f}")
        print("最佳参数:")
        for key, value in best_params.items():
            print(f"  {key}: {value:.4f}")
    
    elif args.mode == 'evaluate':
        if args.params is None:
            print("请指定参数文件: --params best_params.json")
            return
        
        with open(args.params, 'r') as f:
            params = json.load(f)
        
        evaluator = Evaluator(scenarios)
        result = evaluator.evaluate(params)
        
        print("评估结果:")
        print(f"成功率: {result['success_rate']:.4f}")
        print(f"平均路径长度: {result['avg_path_length']:.4f}")
        print(f"平均规划时间: {result['avg_plan_time_ms']:.4f} ms")
        
        for i, detail in enumerate(result['details']):
            print(f"\n场景 {i+1}:")
            print(f"  成功: {detail['success']}")
            print(f"  路径长度: {detail['path_length']:.4f}")
            print(f"  步数: {detail['steps']}")
    
    elif args.mode == 'demo':
        from .planner import DWAConfig, plan_path
        import numpy as np
        
        config = DWAConfig()
        start = [0.0, 0.0, np.pi / 2.0]
        goal = [10.0, 10.0]
        obstacles = np.array([[3.0, 3.0], [5.0, 5.0], [7.0, 7.0]])
        
        print("DWA 路径规划演示")
        print(f"起点: {start[:2]}")
        print(f"目标: {goal}")
        print(f"障碍物数量: {len(obstacles)}")
        
        trajectory, steps, dist_to_goal = plan_path(start, goal, obstacles, config)
        
        print(f"\n规划完成!")
        print(f"总步数: {steps}")
        print(f"最终距离目标: {dist_to_goal:.4f}")
        print(f"路径长度: {np.sum(np.sqrt(np.diff(trajectory[:, 0])**2 + np.diff(trajectory[:, 1])**2)):.4f}")

if __name__ == '__main__':
    main()