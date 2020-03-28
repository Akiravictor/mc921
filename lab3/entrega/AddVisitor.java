import java.util.HashMap;

public class AddVisitor extends SummerBaseVisitor<Integer> {
    HashMap <String, String> declare = new HashMap <String, String>();
    HashMap <String, String> function = new HashMap <String, String>();
    HashMap <String, Integer> numParameters = new HashMap <String, Integer>();
    
    @Override
    public Integer visitRoot(SummerParser.RootContext ctx){
    	return visitChildren(ctx);
    }
    
    @Override
    public Integer visitDeclareVar(SummerParser.DeclareVarContext ctx){
    	String id = ctx.ID().getText();
    	
    	//System.out.println("DeclareVar: " + id + " " + ctx.expr().getText());
    	
    	if (!declare.containsKey(id)){
    		declare.put(id, "var");
    		visit(ctx.expr());
    	}
    	else {
    		System.out.println("Symbol already declared: " + id);
    	}
    	
    	return 0;
    }
    
    @Override
    public Integer visitDeclareFunc(SummerParser.DeclareFuncContext ctx){
    	String id = ctx.ID().getText();
    	
    	//System.out.println("DeclareFunc: " + id + " " + ctx.args().getText() + " " + ctx.expr().getText());
    	
    	if (!declare.containsKey(id)){
    		declare.put(id, "func");
    		numParameters.put(id, visit(ctx.args()));
    		
    		//System.out.println("DeclareFunc: " + numParameters.get(id));
    		
    		visit(ctx.expr());
    	}
    	else {	
    		System.out.println("Symbol already declared: " + id);
    	}
    	
    	function.clear();
    	
    	return 0;
    }
    
    @Override
    public Integer visitArgId(SummerParser.ArgIdContext ctx) {
    	String id = ctx.ID().getText();
    	
    	if (function.containsKey(id)) {
    		System.out.println("Symbol already declared: " + id);
    	}
    	else {
    		function.put(id, "arg");
    	}
    	
    	return 1;
    }
    
    @Override
    public Integer visitMultArg(SummerParser.MultArgContext ctx) {
    	String id = ctx.ID().getText();
    	
    	if (function.containsKey(id)) {
    		System.out.println("Symbol already declared: " + id);
    	}
    	else {
    		function.put(id, "arg");
    	}
    	
    	return 1 + visit(ctx.args());
    }
    
    @Override
    public Integer visitIDOnly(SummerParser.IDOnlyContext ctx) {
    	return 1;
    }
    
    @Override
    public Integer visitNUMOnly(SummerParser.NUMOnlyContext ctx) {
    	return 1;
    }
    
    @Override
    public Integer visitIDParameter(SummerParser.IDParameterContext ctx) {
    	return 1 + visit(ctx.prmt());
    }
    
    @Override
    public Integer visitNUMParameter(SummerParser.NUMParameterContext ctx) {
    	return 1 + visit(ctx.prmt());
    }
    
    @Override
    public Integer visitParamFunc(SummerParser.ParamFuncContext ctx) {
    	return 1 + visit(ctx.fUse());
    }
    
    @Override
    public Integer visitFuncUse(SummerParser.FuncUseContext ctx) {
    	String id = ctx.ID().getText();
    	
    	if (declare.containsKey(id) && declare.get(id).equals("func")) {
    		if (visit(ctx.prmt()) != numParameters.get(id)) {
    			System.out.println("Bad argument count: " + id);
    		}
    	}
    	else if (declare.containsKey(id) && !declare.get(id).equals("func")) {
    		System.out.println("Bad used symbol: " + id);
    	}
    	else {
    		System.out.println("Symbol undeclared: " + id);
    	}
    	
    	return 0;
    }
    
    @Override
    public Integer visitIDExpr(SummerParser.IDExprContext ctx) {
    	String id = ctx.ID().getText();
    	
    	//System.out.println("IDExpr: " + id);
    	//System.out.println("IDExpr: declare: " + declare.toString());
    	//System.out.println("IDExpr: function: " + function.toString());
    	
    	if (!declare.containsKey(id) && !function.containsKey(id)) {
    		System.out.println("Symbol undeclared: " + id);
    	}
    	else if (declare.containsKey(id) && !function.containsKey(id) && declare.get(id).equals("func")) {
    		System.out.println("Bad used symbol: " + id);
    	}
    	
    	
    	return 0;
    }
    
}
