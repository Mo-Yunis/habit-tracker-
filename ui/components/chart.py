import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=2, dpi=100, theme_colors=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.theme_colors = theme_colors or {}
        bg_color = self.theme_colors.get("chart_bg", "#282a36")
        
        fig.patch.set_facecolor(bg_color)
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor(bg_color)
        
        super(DashboardChart, self).__init__(fig)
        self.setStyleSheet("background-color: transparent;")

    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        bg_color = self.theme_colors.get("chart_bg", "#282a36")
        self.figure.patch.set_facecolor(bg_color)
        self.axes.set_facecolor(bg_color)
        self.draw()

    def plot(self, habits, graph_type="Horizontal Bar", view_mode="Entire Month"):
        self.axes.clear()
        self.axes.axis('auto')
        
        text_color = self.theme_colors.get("chart_text", "#f8f8f2")
        grid_color = self.theme_colors.get("chart_grid", "#44475a")
        accent = self.theme_colors.get("accent", "#bd93f9")
        accent_hover = self.theme_colors.get("accent_hover", "#ff79c6")
        
        if not habits:
            self.axes.text(0.5, 0.5, "No habits added yet.", 
                           color=text_color, fontsize=14, 
                           ha='center', va='center')
            self.axes.axis('off')
            self.draw()
            return
            
        names = []
        percentages = []
        colors = []
        
        from datetime import datetime
        now = datetime.now()
        current_day = now.day
        
        for h in habits:
            logs = h["logs"]
            daily_target = h["daily_target"]
            
            if view_mode == "Today":
                today_completed = next((val for d, val in logs if d == current_day), 0)
                pct = (today_completed / daily_target) * 100 if daily_target > 0 else 0
                if pct > 100: pct = 100
            else:
                if h["type"] == "daily":
                    days_met = sum(1 for x in logs if x[1] >= daily_target)
                    total_days = len(logs)
                    pct = (days_met / total_days) * 100 if total_days > 0 else 0
                else:
                    total_reps = sum(x[1] for x in logs)
                    tot_target = h["total_target"]
                    pct = (total_reps / tot_target) * 100 if tot_target > 0 else 0
                    if pct > 100: pct = 100

            names.append(h["name"])
            percentages.append(pct)
            colors.append(accent if pct >= 100 else accent_hover)

        if graph_type == "Pie Chart":
            reps = []
            for h in habits:
                if view_mode == "Today":
                    today_val = next((val for d, val in h["logs"] if d == current_day), 0)
                    reps.append(today_val)
                else:
                    reps.append(sum(x[1] for x in h["logs"]))
            if sum(reps) == 0:
                 self.axes.text(0.5, 0.5, "No data yet.", color=text_color, ha='center', va='center')
                 self.axes.axis('off')
            else:
                 palette = self.theme_colors.get("palette", [accent, accent_hover, "#8be9fd", "#50fa7b", "#f1fa8c"])
                 pie_colors = [palette[i % len(palette)] for i in range(len(names))]
                 self.axes.pie(reps, labels=names, colors=pie_colors, autopct='%1.1f%%', textprops={'color': text_color})
                 self.axes.axis('equal')
        elif graph_type == "Vertical Bar":
            x_pos = range(len(names))
            self.axes.bar(x_pos, percentages, color=colors, width=0.5)
            self.axes.set_xticks(x_pos)
            self.axes.set_xticklabels(names, color=text_color, fontsize=10, rotation=45, ha='right')
            self.axes.set_ylabel("Completion %", color=text_color, fontsize=10)
            self.axes.set_ylim(0, 100)
            self.axes.tick_params(colors=text_color)
            for spine in self.axes.spines.values():
                spine.set_edgecolor(grid_color)
        else: # Horizontal Bar
            y_pos = range(len(names))
            self.axes.barh(y_pos, percentages, color=colors, height=0.5)
            self.axes.set_yticks(y_pos)
            self.axes.set_yticklabels(names, color=text_color, fontsize=10)
            self.axes.set_xlabel("Completion %", color=text_color, fontsize=10)
            self.axes.set_xlim(0, 100)
            self.axes.tick_params(colors=text_color)
            for spine in self.axes.spines.values():
                spine.set_edgecolor(grid_color)

        self.figure.tight_layout()
        self.draw()
