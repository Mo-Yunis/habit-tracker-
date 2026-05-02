import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardChart(FigureCanvas):
    def __init__(self, parent=None, width=10, height=3, dpi=100, theme_colors=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.theme_colors = theme_colors or {}
        bg_color = self.theme_colors.get("chart_bg", "#1E1E2E")
        
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0)
        
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('none')
        
        super(DashboardChart, self).__init__(fig)
        self.setStyleSheet("background-color: transparent;")

    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.draw()

    def plot(self, habits, graph_type="Horizontal Bar", view_mode="Entire Month"):
        self.axes.clear()
        self.axes.axis('auto')
        
        text_color = self.theme_colors.get("text_main", "#F8F8F2")
        muted_color = self.theme_colors.get("text_muted", "#9499C3")
        grid_color = self.theme_colors.get("chart_grid", "#44475A")
        accent = self.theme_colors.get("accent", "#BD93F9")
        accent_hover = self.theme_colors.get("accent_hover", "#FF79C6")
        
        if not habits:
            self.axes.text(0.5, 0.5, "No habits yet. Add one to see analytics!", 
                           color=muted_color, fontsize=12, fontweight='bold',
                           ha='center', va='center')
            self.axes.axis('off')
            self.draw()
            return
            
        names = []
        percentages = []
        colors = []
        
        from datetime import datetime
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        for h in habits:
            logs = h["logs"]
            daily_target = h["daily_target"]
            
            if view_mode == "Today":
                today_completed = next((val for d, val, ld in logs if ld == today_str), 0)
                pct = (today_completed / daily_target) * 100 if daily_target > 0 else 0
                if pct > 100: pct = 100
            else:
                if h["type"] == "daily":
                    days_met = sum(1 for d, val, ld in logs if val >= daily_target)
                    total_days = len(logs)
                    pct = (days_met / total_days) * 100 if total_days > 0 else 0
                else:
                    total_reps = sum(val for d, val, ld in logs)
                    tot_target = h["total_target"]
                    pct = (total_reps / tot_target) * 100 if tot_target > 0 else 0
                    if pct > 100: pct = 100

            names.append(h["name"])
            percentages.append(pct)
            colors.append(accent if pct < 100 else "#50FA7B")

        if graph_type == "Pie Chart":
            reps = []
            for h in habits:
                if view_mode == "Today":
                    today_val = next((val for d, val, ld in h["logs"] if ld == today_str), 0)
                    reps.append(today_val)
                else:
                    reps.append(sum(val for d, val, ld in h["logs"]))
            
            if sum(reps) == 0:
                 self.axes.text(0.5, 0.5, "Log some progress first!", color=muted_color, ha='center', va='center', fontweight='bold')
                 self.axes.axis('off')
            else:
                 palette = self.theme_colors.get("palette", [accent, accent_hover, "#8BE9FD", "#50FA7B"])
                 pie_colors = [palette[i % len(palette)] for i in range(len(names))]
                 patches, texts, autotexts = self.axes.pie(reps, labels=names, colors=pie_colors, 
                                                         autopct='%1.0f%%', pctdistance=0.8,
                                                         textprops={'color': text_color, 'fontweight': 'bold'})
                 for text in texts: text.set_fontsize(9)
                 for autotext in autotexts: autotext.set_fontsize(8)
                 self.axes.axis('equal')
        
        elif graph_type == "Vertical Bar":
            x_pos = range(len(names))
            bars = self.axes.bar(x_pos, percentages, color=colors, width=0.6, edgecolor='none')
            self.axes.set_xticks(x_pos)
            self.axes.set_xticklabels(names, color=text_color, fontsize=9, rotation=0, ha='center')
            self.axes.set_ylim(0, 110)
            self.axes.tick_params(colors=muted_color, labelsize=8)
            for spine in self.axes.spines.values(): spine.set_visible(False)
            self.axes.grid(axis='y', color=grid_color, linestyle='--', alpha=0.3)
            
        else: # Horizontal Bar
            y_pos = range(len(names))
            self.axes.barh(y_pos, percentages, color=colors, height=0.6)
            self.axes.set_yticks(y_pos)
            self.axes.set_yticklabels(names, color=text_color, fontsize=9)
            self.axes.set_xlim(0, 110)
            self.axes.tick_params(colors=muted_color, labelsize=8)
            for spine in self.axes.spines.values(): spine.set_visible(False)
            self.axes.grid(axis='x', color=grid_color, linestyle='--', alpha=0.3)

        self.figure.tight_layout()
        self.draw()
